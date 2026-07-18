from ..converters.base import BaseConverter, FileCategory


class ConverterRegistry:
    _converters: list[type[BaseConverter]] = []

    @classmethod
    def register(cls, converter_class: type[BaseConverter]) -> type[BaseConverter]:
        if converter_class not in cls._converters:
            cls._converters.append(converter_class)
        return converter_class

    @classmethod
    def get_converter(cls, source_ext: str, target_ext: str) -> BaseConverter | None:
        for conv_cls in cls._converters:
            if conv_cls.can_convert(source_ext, target_ext):
                return conv_cls()
        return None

    @classmethod
    def get_valid_outputs(cls, source_ext: str) -> list[str]:
        outputs = set()
        for conv_cls in cls._converters:
            outputs.update(conv_cls.get_valid_outputs(source_ext))
        return sorted(outputs)

    @classmethod
    def get_category(cls, ext: str) -> FileCategory:
        ext = ext.lower().lstrip(".")
        for conv_cls in cls._converters:
            if ext in conv_cls.SUPPORTED_INPUT:
                return conv_cls.CATEGORY
        return FileCategory.UNKNOWN

    @classmethod
    def get_converter_for_category(cls, category: FileCategory) -> BaseConverter | None:
        for conv_cls in cls._converters:
            if conv_cls.CATEGORY == category:
                return conv_cls()
        return None

    @classmethod
    def get_all_converters(cls) -> list[type[BaseConverter]]:
        return list(cls._converters)

    @classmethod
    def get_supported_extensions(cls) -> dict[FileCategory, list[str]]:
        result: dict[FileCategory, set[str]] = {}
        for conv_cls in cls._converters:
            cat = conv_cls.CATEGORY
            if cat not in result:
                result[cat] = set()
            result[cat].update(conv_cls.SUPPORTED_INPUT)
        return {cat: sorted(exts) for cat, exts in result.items()}
