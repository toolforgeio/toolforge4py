from os import path

from yaml import safe_load


class ManifestEnvironmentSecret:
    @staticmethod
    def from_yaml(o):
        return ManifestEnvironmentSecret(o.get("name"), o.get("description"), o.get("required"), o.get("example"))

    def __init__(self, name: str, description: str, required: bool, example: str):
        self.name = name
        self.description = description
        self.required = required
        self.example = example

    def __eq__(self, other):
        return (self.name == other.name
                and self.description == other.description
                and self.required == other.required
                and self.example == other.example)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"ManifestEnvironmentSecret({self.name}, {self.description}, {self.required}, {self.example})"


class ManifestEnvironmentVariable:
    @staticmethod
    def from_yaml(o):
        return ManifestEnvironmentVariable(o.get("name"), o.get("description"), o.get("required"), o.get("default"))

    def __init__(self, name: str, description: str, required: bool, default: str):
        self.name = name
        self.description = description
        self.required = required
        self.default = default

    def __eq__(self, other):
        return (self.name == other.name
                and self.description == other.description
                and self.required == other.required
                and self.default == other.default)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"ManifestEnvironmentVariable({self.name}, {self.description}, {self.required}, {self.default})"


class ManifestEnvironment:
    @staticmethod
    def from_yaml(o):
        return ManifestEnvironment(o.get("size"),
                                   [ManifestEnvironmentSecret.from_yaml(e) for e in o.get("secrets", [])],
                                   [ManifestEnvironmentVariable.from_yaml(e) for e in o.get("variables", [])])

    def __init__(self, size: str, secrets: list[ManifestEnvironmentSecret],
                 variables: list[ManifestEnvironmentVariable]):
        self.size = size
        self.secrets = secrets
        self.variables = variables

    def __eq__(self, other):
        return (self.size == other.size
                and self.secrets == other.secrets
                and self.variables == other.variables)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"ManifestEnvironment({self.size}, {self.secrets}, {self.variables})"


class Manifest:
    @staticmethod
    def discover():
        """
        Find and load manifest from well-known locations
        :return: The discovered Manifest
        """
        for filename in ["/toolforge/manifest.yml", "manifest.yml"]:
            if path.isfile(filename):
                with open(filename, "r") as f:
                    return Manifest.loads(f.read())
        raise FileNotFoundError()

    @staticmethod
    def from_yaml(o):
        """
        Load a Manifest from the given parsed yaml data
        :param o:
        :return:
        """
        type = o.get("type")
        if type == "tool":
            return ToolManifest.from_yaml(o)
        raise ValueError(f"unrecognized type {type}")

    @staticmethod
    def loads(s: str):
        """
        Parse the given string as yaml data, then load a Manifest from it.
        :param s:
        :return:
        """
        return Manifest.from_yaml(safe_load(s))

    def __init__(self, toolforge: str, type: str, container: str, environment: ManifestEnvironment):
        self.toolforge = toolforge
        self.type = type
        self.container = container
        self.environment = environment

    def __eq__(self, other):
        return (self.toolforge == other.toolforge
                and self.type == other.type
                and self.container == other.container
                and self.environment == other.environment)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"Manifest({self.toolforge}, {self.type}, {self.container}, {self.environment})"


class ToolManifestParameter:
    @staticmethod
    def from_yaml(o):
        return ToolManifestParameter(o.get("type"), o.get("name"), o.get("description"), o.get("required"))

    def __init__(self, type: str, name: str, description: str, required: bool):
        self.type = type
        self.name = name
        self.description = description
        self.required = required

    def __eq__(self, other):
        return (self.type == other.type
                and self.name == other.name
                and self.description == other.description
                and self.required == other.required)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"ToolManifestParameter({self.type}, {self.name}, {self.description}, {self.required})"


class ToolManifestSlot:
    @staticmethod
    def from_yaml(o):
        return ToolManifestSlot(o.get("name"), o.get("description"), o.get("extensions", []))

    def __init__(self, name: str, description: str, extensions: list[str]):
        self.name = name
        self.description = description
        self.extensions = extensions

    def __eq__(self, other):
        return (self.name == other.name
                and self.description == other.description
                and self.extensions == other.extensions)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"ToolManifestSlot({self.name}, {self.description}, {self.extensions})"


class ToolManifest(Manifest):
    @staticmethod
    def from_yaml(o):
        if o.get("type") != "tool":
            raise ValueError(f"unexpected type {o.get('type')}")
        return ToolManifest(o.get("toolforge"), o.get("container"),
                            ManifestEnvironment.from_yaml(o.get("environment", {})),
                            [ToolManifestParameter.from_yaml(e) for e in o.get("parameters", [])],
                            [ToolManifestSlot.from_yaml(e) for e in o.get("inputs", [])],
                            [ToolManifestSlot.from_yaml(e) for e in o.get("outputs", [])])

    def __init__(self, toolforge: str, container: str, environment: ManifestEnvironment,
                 parameters: list[ToolManifestParameter], inputs:
            list[ToolManifestSlot], outputs: list[ToolManifestSlot]):
        super().__init__(toolforge, "tool", container, environment)
        self.parameters = parameters
        self.inputs = inputs
        self.outputs = outputs

    def __eq__(self, other):
        return (super().__eq__(other)
                and self.parameters == other.parameters
                and self.inputs == other.inputs
                and self.outputs == other.outputs)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"ToolManifest({self.toolforge}, {self.type}, {self.container}, {self.environment}, {self.parameters}, {self.inputs}, {self.outputs})"
