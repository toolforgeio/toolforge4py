import os
import unittest
from pathlib import Path

from toolforgeio.io import read_input_spreadsheet_data_frame

current_path = Path(os.path.dirname(os.path.realpath(__file__)))

image_path = current_path / "images" / "fernando1.jpg"


class ArgumentsTests(unittest.TestCase):
    def test_read_spreadsheet(self):
        for filename in ["legacy.xls", "ooxml.xlsx", "with-bom.csv", "without-bom-utf-8.csv"]:
            filepath = current_path / "spreadsheets" / filename
            df = read_input_spreadsheet_data_frame(f"file://{filepath}")
            rows = [list(df.columns)] + list(df.apply(lambda r: [r[0], r[1]], axis=1))
            self.assertEqual(rows, [["hello", "world"], ["alpha", "bravo"]])

    def test_good_sheet_hint(self):
        for filename in ["legacy.xls", "ooxml.xlsx"]:
            filepath = current_path / "spreadsheets" / filename
            df = read_input_spreadsheet_data_frame(f"file://{filepath}", sheet_hint="with-bom")
            rows = [list(df.columns)] + list(df.apply(lambda r: [r[0], r[1]], axis=1))
            self.assertEqual(rows, [["hello", "world"], ["alpha", "bravo"]])

    def test_bad_sheet_hint(self):
        for filename in ["legacy.xls", "ooxml.xlsx"]:
            filepath = current_path / "spreadsheets" / filename
            df = read_input_spreadsheet_data_frame(f"file://{filepath}", sheet_hint="foobar")
            rows = [list(df.columns)] + list(df.apply(lambda r: [r[0], r[1]], axis=1))
            self.assertEqual(rows, [["hello", "world"], ["alpha", "bravo"]])

    def test_good_sheet_hint_multisheet(self):
        for filename in ["multisheet.xlsx"]:
            filepath = current_path / "spreadsheets" / filename
            df = read_input_spreadsheet_data_frame(f"file://{filepath}", sheet_hint="bravo")
            rows = [list(df.columns)] + list(df.apply(lambda r: [r[0], r[1]], axis=1))
            self.assertEqual(rows, [["hello", "world"], ["alpha", "bravo"]])
