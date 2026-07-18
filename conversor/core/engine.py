import uuid
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable
from datetime import datetime

from ..converters.base import ConversionTask, ConversionStatus, ConversionOptions, FileCategory
from .registry import ConverterRegistry
from .validation import validate_conversion
from ..utils.logger import logger
from ..utils.config import config_manager, ConversionRecord


class ConversionEngine:
    def __init__(self, max_workers: int = 3):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._tasks: dict[str, ConversionTask] = {}
        self._futures: dict[str, Future] = {}
        self._task_start_times: dict[str, float] = {}
        self._task_durations: dict[str, float] = {}
        self._lock = threading.Lock()
        self._on_task_update: Callable | None = None
        self._cancelled = False
        self._max_retries = config_manager.get_config().max_retries

    def set_on_task_update(self, callback: Callable):
        self._on_task_update = callback

    def create_task(
        self,
        source_path: Path,
        output_format: str,
        options: ConversionOptions | None = None,
    ) -> ConversionTask:
        ext = source_path.suffix.lower().lstrip(".")
        category = ConverterRegistry.get_category(ext)

        task = ConversionTask(
            id=str(uuid.uuid4())[:8],
            source_path=source_path,
            output_format=output_format,
            category=category,
            options=options or ConversionOptions(output_format=output_format),
        )

        with self._lock:
            self._tasks[task.id] = task

        return task

    def submit_task(self, task: ConversionTask) -> str:
        def _run():
            start_time = time.time()
            with self._lock:
                self._task_start_times[task.id] = start_time

            max_attempts = self._max_retries + 1
            last_error = None

            for attempt in range(1, max_attempts + 1):
                try:
                    with self._lock:
                        task.status = ConversionStatus.IN_PROGRESS
                        task.progress = 0.0

                    if self._on_task_update:
                        self._on_task_update(task)

                    logger.log_conversion_start(task.source_path, task.output_format)

                    validation = validate_conversion(
                        task.source_path,
                        task.output_format,
                        Path(task.options.output_dir) if task.options.output_dir else None
                    )
                    if not validation.valid:
                        raise ValueError(f"Validación fallida: {validation.error_message}")

                    converter = ConverterRegistry.get_converter(
                        task.source_path.suffix, task.output_format
                    )
                    if not converter:
                        raise ValueError(
                            f"No se puede convertir {task.source_path.suffix} a {task.output_format}"
                        )

                    def on_progress(value: float):
                        with self._lock:
                            task.progress = value
                        if self._on_task_update:
                            self._on_task_update(task)

                    task.on_progress = on_progress
                    output_path = converter.convert(task)

                    duration = time.time() - start_time
                    with self._lock:
                        task.output_path = output_path
                        task.status = ConversionStatus.COMPLETED
                        task.progress = 1.0
                        self._task_durations[task.id] = duration

                    logger.log_conversion_success(task.source_path, output_path, duration)
                    self._record_history(task, "completed", duration)
                    break

                except Exception as e:
                    last_error = str(e)
                    logger.log_conversion_error(task.source_path, last_error, attempt)

                    if attempt < max_attempts:
                        logger.log_retry(task.source_path, attempt + 1, max_attempts)
                        with self._lock:
                            task.status = ConversionStatus.IN_PROGRESS
                            task.progress = 0.0
                            task.error_message = f"Reintentando ({attempt + 1}/{max_attempts})..."
                        if self._on_task_update:
                            self._on_task_update(task)
                        time.sleep(1)
                    else:
                        with self._lock:
                            task.status = ConversionStatus.FAILED
                            task.error_message = last_error

                        duration = time.time() - start_time
                        with self._lock:
                            self._task_durations[task.id] = duration

                        logger.error(f"Conversión fallida después de {max_attempts} intentos: {task.source_path.name}")
                        self._record_history(task, "failed", duration, last_error)

            if self._on_task_update:
                self._on_task_update(task)

        future = self._executor.submit(_run)
        with self._lock:
            self._futures[task.id] = future

        return task.id

    def submit_batch(self, tasks: list[ConversionTask]) -> list[str]:
        ids = []
        for task in tasks:
            task_id = self.submit_task(task)
            ids.append(task_id)
        return ids

    def _record_history(self, task: ConversionTask, status: str, duration: float, error: str = ""):
        try:
            source_size = task.source_path.stat().st_size if task.source_path.exists() else 0
            output_size = task.output_path.stat().st_size if task.output_path and task.output_path.exists() else 0

            record = ConversionRecord(
                id=task.id,
                source_path=str(task.source_path),
                output_path=str(task.output_path) if task.output_path else "",
                source_format=task.source_path.suffix.lstrip("."),
                output_format=task.output_format,
                category=task.category.value,
                status=status,
                timestamp=datetime.now().isoformat(),
                duration=duration,
                file_size_before=source_size,
                file_size_after=output_size,
                error_message=error,
            )
            config_manager.add_to_history(record)
        except Exception as e:
            logger.error(f"Error al registrar historial: {e}")

    def cancel_task(self, task_id: str):
        with self._lock:
            future = self._futures.get(task_id)
            task = self._tasks.get(task_id)
            if future and task and task.status == ConversionStatus.PENDING:
                future.cancel()
                task.status = ConversionStatus.CANCELLED
                if self._on_task_update:
                    self._on_task_update(task)

    def cancel_all(self):
        with self._lock:
            self._cancelled = True
            for task_id, task in self._tasks.items():
                if task.status in (ConversionStatus.PENDING, ConversionStatus.IN_PROGRESS):
                    future = self._futures.get(task_id)
                    if future:
                        future.cancel()
                    task.status = ConversionStatus.CANCELLED
                    if self._on_task_update:
                        self._on_task_update(task)

    def get_task(self, task_id: str) -> ConversionTask | None:
        with self._lock:
            return self._tasks.get(task_id)

    def get_all_tasks(self) -> list[ConversionTask]:
        with self._lock:
            return list(self._tasks.values())

    def get_pending_tasks(self) -> list[ConversionTask]:
        with self._lock:
            return [t for t in self._tasks.values() if t.status == ConversionStatus.PENDING]

    def get_active_tasks(self) -> list[ConversionTask]:
        with self._lock:
            return [t for t in self._tasks.values()
                    if t.status in (ConversionStatus.PENDING, ConversionStatus.IN_PROGRESS)]

    def clear_completed(self):
        with self._lock:
            to_remove = [
                tid for tid, t in self._tasks.items()
                if t.status in (ConversionStatus.COMPLETED, ConversionStatus.FAILED, ConversionStatus.CANCELLED)
            ]
            for tid in to_remove:
                del self._tasks[tid]
                self._futures.pop(tid, None)
                self._task_start_times.pop(tid, None)
                self._task_durations.pop(tid, None)

    def reset(self):
        with self._lock:
            self._tasks.clear()
            self._futures.clear()
            self._task_start_times.clear()
            self._task_durations.clear()
            self._cancelled = False

    def shutdown(self, wait: bool = True):
        self._executor.shutdown(wait=wait)

    @property
    def task_count(self) -> int:
        with self._lock:
            return len(self._tasks)

    def get_summary(self) -> dict:
        with self._lock:
            summary = {
                "total": len(self._tasks),
                "pending": 0,
                "in_progress": 0,
                "completed": 0,
                "failed": 0,
                "cancelled": 0,
            }
            for task in self._tasks.values():
                summary[task.status.value] = summary.get(task.status.value, 0) + 1
            return summary

    def get_estimated_time_remaining(self) -> float:
        with self._lock:
            if not self._task_durations:
                return 0.0

            avg_duration = sum(self._task_durations.values()) / len(self._task_durations)
            pending_count = sum(1 for t in self._tasks.values() if t.status == ConversionStatus.PENDING)
            in_progress_count = sum(1 for t in self._tasks.values() if t.status == ConversionStatus.IN_PROGRESS)

            return (pending_count * avg_duration) + (avg_duration * 0.5 * in_progress_count)

    def move_task_up(self, task_id: str):
        pass

    def move_task_down(self, task_id: str):
        pass
