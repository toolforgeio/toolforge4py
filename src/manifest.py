from json import loads
from os import path


class ManifestEnvironmentSecret:
    @staticmethod
    def from_json(o):
        return ManifestEnvironmentSecret(o.get("name"), o.get("description"), o.get("required"), o.get("example"))

    def __init__(self, name: str, description: str, required: bool, example: str):
        self.name = name
        self.description = description
        self.required = required
        self.example = example


class ManifestEnvironmentVariable:
    @staticmethod
    def from_json(o):
        return ManifestEnvironmentVariable(o.get("name"), o.get("description"), o.get("required"), o.get("default"))

    def __init__(self, name: str, description: str, required: bool, default: str):
        self.name = name
        self.description = description
        self.required = required
        self.default = default


class ManifestEnvironment:
    @staticmethod
    def from_json(o):
        return ManifestEnvironment(o.get("size"), [ManifestEnvironmentSecret(e) for e in o.get("secrets", [])],
                                   [ManifestEnvironmentVariable(e) for e in o.get("variables", [])])

    def __init__(self, size: str, secrets: list[ManifestEnvironmentSecret],
                 variables: list[ManifestEnvironmentVariable]):
        self.size = size
        self.secrets = secrets
        self.variables = variables


class Manifest:
    @staticmethod
    def discover():
        """
        Find and load manifest from well-known locations
        :return: The discovered Manifest
        """
        for filename in [ "/toolforge/manifest.yml", "manifest.yml" ]:
            if path.isfile(filename):
                with open(filename, "r") as f:
                    return Manifest.loads(f.read())
        raise FileNotFoundError()

    @staticmethod
    def from_json(o):
        """
        Load a Manifest from the given parsed JSON data
        :param o:
        :return:
        """
        type = o.get("type")
        if type == "tool":
            return ToolManifest.from_json(o)
        raise ValueError(f"unrecognized type {type}")

    @staticmethod
    def loads(s: str):
        """
        Parse the given string as JSON data, then load a Manifest from it.
        :param s:
        :return:
        """
        return Manifest.from_json(loads(s))

    def __init__(self, toolforge: str, type: str, container: str, environment: ManifestEnvironment):
        self.toolforge = toolforge
        self.type = type
        self.container = container
        self.environment = environment


class ToolManifestParameter:
    @staticmethod
    def from_json(o):
        return ToolManifestParameter(o.get("type"), o.get("name"), o.get("description"), o.get("required"))

    def __init__(self, type: str, name: str, description: str, required: bool):
        self.type = type
        self.name = name
        self.description = description
        self.required = required


class ToolManifestSlot:
    @staticmethod
    def from_json(o):
        return ToolManifestSlot(o.get("name"), o.get("description"), o.get("extensions", []))

    def __init__(self, name: str, description: str, extensions: list[str]):
        self.name = name
        self.description = description
        self.extensions = extensions


class ToolManifest(Manifest):
    @staticmethod
    def from_json(o):
        if o.get("type") != "tool":
            raise ValueError(f"unexpected type {o.get('type')}")
        return ToolManifest(o.get("toolforge"), o.get("container"),
                            ManifestEnvironment.from_json(o.get("environment", {})),
                            [ToolManifestParameter.from_json(e) for e in o.get("parameters", [])],
                            [ToolManifestSlot.from_json(e) for e in o.get("inputs", [])],
                            [ToolManifestSlot.from_json(e) for e in o.get("outputs", [])])

    def __init__(self, toolforge: str, container: str, environment: ManifestEnvironment,
                 parameters: list[ToolManifestParameter], inputs:
            list[ToolManifestSlot], outputs: list[ToolManifestSlot]):
        super().__init__(toolforge, "tool", container, environment)
        self.parameters = parameters
        self.inputs = inputs
        self.outputs = outputs