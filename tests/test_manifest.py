import unittest

from toolforgeio.manifest import *


class ManifestTests(unittest.TestCase):
    def test_loads(self):
        """ Manifest.loads() should work nicely """
        m = Manifest.loads("""
            toolforge: 1.0
            container: abcd1234
            type: tool
            environment:
              size: medium
              secrets:
                - name: SECRET
                  description: Secret Description
                  example: hello
                  required: true
              variables:
                - name: VARIABLE
                  description: Variable Description
                  default: world
                  required: false
            parameters:
              - type: int
                name: IntParameter
                description: Int Description
                required: true
              - type: float
                name: FloatParameter
                description: Float Description
                required: true
            inputs:
              - name: Input
                description: Input Description
                required: true
                extensions:
                  - txt
                  - csv
                  - xls
                  - xlsx
            outputs:
              - name: Output
                description: Output Description
                required: false
                extensions:
                  - csv
                  - xlsx
            """)

        self.assertEqual(m, ToolManifest(
            1.0,
            "abcd1234",
            ManifestEnvironment(
                "medium",
                [ManifestEnvironmentSecret("SECRET", "Secret Description", True, "hello")],
                [ManifestEnvironmentVariable("VARIABLE", "Variable Description", False, "world")]),
            [ToolManifestParameter("int", "IntParameter", "Int Description", True),
             ToolManifestParameter("float", "FloatParameter", "Float Description", True)],
            [ToolManifestSlot("Input", "Input Description", ["txt", "csv", "xls", "xlsx"])],
            [ToolManifestSlot("Output", "Output Description", ["csv", "xlsx"])]))


if __name__ == '__main__':
    unittest.main()
