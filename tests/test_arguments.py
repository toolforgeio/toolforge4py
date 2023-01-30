import datetime
import unittest

from toolforgeio.arguments import *
from toolforgeio.manifest import *


class ArgumentsTests(unittest.TestCase):
    def test_parse(self):
        args = Arguments.parse_from_argv(["python3", "--Alpha", "alpha", "--Bravo.xlsx", "bravo"])

        self.assertEqual(args.get("Alpha"), "alpha")
        self.assertEqual(args.get("Bravo.xlsx"), "bravo")
        self.assertEqual(args.get("Charlie"), None)
        self.assertEqual(args.get("Charlie", "charlie"), "charlie")

    def test_specialize(self):
        manifest = ToolManifest(
            1.0,
            "abcd1234",
            ManifestEnvironment(
                "medium",
                [ManifestEnvironmentSecret("SECRET", "Secret Description", True, "hello")],
                [ManifestEnvironmentVariable("VARIABLE", "Variable Description", False, "world")]),
            [ToolManifestParameter("int", "IntParameter", "Int Description", True),
             ToolManifestParameter("float", "FloatParameter", "Float Description", True),
             ToolManifestParameter("date", "DateParameter", "Date Description", True),
             ToolManifestParameter("boolean", "BooleanParameter", "Boolean Description", True),
             ToolManifestParameter("string", "StringParameter", "String Description", True)],
            [ToolManifestSlot("Input", "Input Description", ["txt", "csv", "xls", "xlsx"])],
            [ToolManifestSlot("Output", "Output Description", ["csv", "xlsx"])])

        args = Arguments.parse_from_argv(
            ["python3", "--IntParameter", "10", "--FloatParameter", "1.2", "--DateParameter", "2020-01-01",
             "--BooleanParameter", "true", "--StringParameter", "hello"]).specialize(manifest)

        self.assertEqual(args.get("IntParameter"), 10)
        self.assertEqual(args.get("FloatParameter"), 1.2)
        self.assertEqual(args.get("DateParameter"), datetime(2020, 1, 1, 0, 0))
        self.assertEqual(args.get("BooleanParameter"), True)
        self.assertEqual(args.get("StringParameter"), "hello")
