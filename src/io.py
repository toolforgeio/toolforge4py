from hashlib import md5
from typing import BinaryIO

import requests
from openpyxl import load_workbook
from pandas import read_excel, read_csv

XLSX_MAGIC_NUMBER = b"\x50\x4B"

XLS_MAGIC_NUMBER = b"\xD0\xCF"


def _first_chunk_to_extension(chunk: bytes):
    """
    Returns the file extension of the file being downloaded based on the first few bytes of the
    file. This is not perfect across all files, but among spreadsheet files, it works just fine.

    :param chunk: The first few bytes of the file, at least 2
    :return: The file extension to use when loading the data
    """
    if chunk.startswith(XLSX_MAGIC_NUMBER):
        return "xlsx"
    elif chunk.startswith(XLS_MAGIC_NUMBER):
        return "xls"
    else:
        return "csv"


def read_input_spreadsheet_data_frame(url: str, prefix="/tmp"):
    """
    Downloads a spreadsheet file from the given url and returns a pandas dataframe loaded from the
    resulting data. The type of the spreadsheet is detected automatically, and may be either CSV,
    XLS, or XLSX. If the downloaded spreadsheet contains more than one sheet, then the active sheet
    -- or the sheet that shows on file open -- is returned.

    :param url: The URL from which to download the spreadsheet
    :param prefix: A directory into which to place the downloaded file
    :return: A pandas dataframe containing the data from the spreadsheet
    """

    filename = md5(url.encode(encoding="utf-8")).hexdigest()

    if url.startswith("file://"):
        with open(url[7:], "rb") as fin:
            chunk = fin.read(2)
            extension = _first_chunk_to_extension(chunk)
            filepath = prefix + "/" + filename + "." + extension
            with open(filepath, "wb") as fout:
                fout.write(chunk)
                while chunk := fin.read(4096):
                    fout.write(chunk)
    elif url.startswith("http://") or url.startswith("https://"):
        with requests.get(url, stream=True) as fin:
            iterator = fin.iter_content(4096)
            chunk = next(iterator)
            extension = _first_chunk_to_extension(chunk)
            filepath = prefix + "/" + filename + "." + extension
            with open(filepath, "wb") as fout:
                fout.write(chunk)
                for chunk in iterator:
                    fout.write(chunk)
    else:
        raise ValueError("Unrecognized url protocol", url)

    if extension in ("xls", "xlsx"):
        wb = load_workbook(filepath)
        active_sheet_name = wb.active.title
        print(f"Found Excel workbook, processing active sheet {active_sheet_name}...")
        return read_excel(filepath, sheet_name=active_sheet_name)
    elif extension == "csv":
        print(f"Found CSV file...")
        return read_csv(filepath)
    else:
        raise ValueError("Unrecognized file extension", extension)


def write_output_file(url, data: BinaryIO):
    """
    Uploads output data from the given file-like object to the given URL

    :param url: The destination to which to upload data
    :param data: The data to upload
    """
    requests.put(url, data=data)
