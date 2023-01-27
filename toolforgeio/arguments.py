from __future__ import annotations

from datetime import datetime

from .manifest import Manifest, ToolManifest


class Arguments:
    @staticmethod
    def parse_from_argv(argv) -> Arguments:
        argv = argv[1:]

        options = {}

        for index in range(0, len(argv), 2):
            if index + 1 >= len(argv):
                break
            option = argv[index + 0]
            value = argv[index + 1]

            if not option.startswith("--"):
                raise ValueError(f"unrecognized option {option}")

            options[option[2:]] = value

        return Arguments(options)

    options = None

    def __init__(self, options: dict):
        self.options = options

    def get(self, option, default=None) -> any:
        return self.options.get(option, default)

    def autospecialize(self) -> Arguments:
        """
        Discover the manifest, then specialize this Arguments
        :return: A new Arguments instance with specialized values
        """
        return self.specialize(Manifest.discover())

    def specialize(self, manifest: Manifest) -> Arguments:
        """
        Convert all parameters into their appropriate types as determined by the manifest.

        :param manifest: The tool's manifest
        :return: A new Arguments instance with specialized values
        """
        if isinstance(manifest, ToolManifest):
            options = self.options.copy()
            for parameter in manifest.parameters:
                if parameter.name not in options:
                    continue
                value = options[parameter.name]
                if parameter.type == "int":
                    value = int(value)
                elif parameter.type == "float":
                    value = float(value)
                elif parameter.type == "boolean":
                    value = value.lower().startswith("t")
                elif parameter.type == "string":
                    pass
                elif parameter.type == "date":
                    value = datetime.fromisoformat(value)
                else:
                    raise ValueError(f"unrecognized parameter type {parameter.type}")
                options[parameter.name] = value
            return Arguments(options)
        raise ValueError(f"unrecognized manifest type {manifest.type}")
