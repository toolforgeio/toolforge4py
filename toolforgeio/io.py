from hashlib import md5
from io import TextIOWrapper
from os import SEEK_SET
from typing import BinaryIO, TextIO

import chardet
import openpyxl
import requests
import xlrd
from pandas import read_excel, read_csv, DataFrame

XLSX_MAGIC_NUMBER = b"\x50\x4B"

XLS_MAGIC_NUMBER = b"\xD0\xCF"


def _first_chunk_to_extension(chunk: bytes) -> str:
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


UTF_8_BOM = b"\xEE\xBB\xBF"

UTF_16_BE_BOM = b"\xFE\xFF"

UTF_16_LE_BOM = b"\xFF\xFE"


def _decode(f: BinaryIO, default_encoding="utf-8", min_confidence=0.8, errors="ignore") -> TextIO:
    """
    Decodes the given binary stream into a text stream while ignoring BOMs and detecting character
    sets automatically.

    :param f: The binary stream to decode. Must be seekable.
    :param default_encoding: The default encoding to use if there is no confident match
    :param min_confidence: The minimum confidence to accept in detected character set
    :param errors: How to handle unicode decode errors
    :return: A
    """
    chunk = f.read(3)

    # BOMs have no bearing on the actual content. For example, Excel's "Export to UTF-8 CSV"
    # function prepends a UTF-16 BE BOM on many machines, including the authors. Ignore.
    detected_bom = b''
    for bom in [UTF_8_BOM, UTF_16_LE_BOM, UTF_16_BE_BOM]:
        if chunk.startswith(bom):
            if len(bom) < len(chunk):
                f.seek(len(bom), SEEK_SET)
            detected_bom = bom
            break

    chunk = f.read(128 * 1024)

    f.seek(len(detected_bom), SEEK_SET)

    detected_encoding = chardet.detect(chunk)
    if detected_encoding["confidence"] < min_confidence:
        the_encoding = default_encoding
    else:
        the_encoding = detected_encoding["encoding"]

    return TextIOWrapper(f, encoding=the_encoding, errors=errors)


def read_input_spreadsheet_data_frame(url: str, prefix="/tmp") -> DataFrame:
    """
    Downloads a spreadsheet file from the given url and returns a pandas dataframe loaded from the
    resulting data. The type of the spreadsheet is detected automatically, and may be either CSV,
    XLS, or XLSX. If the downloaded spreadsheet contains more than one sheet, then the active sheet
    -- or the sheet that shows on file open -- is returned.

    :param url: The URL from which to download the spreadsheet
    :param prefix: A directory into which to place the downloaded file
    :return: A pandas dataframe containing the data from the spreadsheet
    """

    # It turns out that the extension of the file when opened is significant,
    # so to avoid the file copy we generate a filename only the fly as we
    # download to reflect the expected file type.

    filename = md5(url.encode(encoding="utf-8")).hexdigest()

    if url.startswith("file://"):
        with open(url[7:], "rb") as fin:
            chunk = fin.read(4096)
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

    if extension == "xlsx":
        wb = openpyxl.load_workbook(filepath)
        active_sheet_name = wb.active.title
        print(f"Found Excel XLSX workbook, processing active sheet {active_sheet_name}...")
        return read_excel(filepath, sheet_name=active_sheet_name)
    elif extension == "xls":
        wb = xlrd.open_workbook(filepath)
        active_sheet_name = [s.name for s in wb.sheets() if s.sheet_visible == 1][0]
        print(f"Found Excel XLS workbook, processing active sheet {active_sheet_name}...")
        return read_excel(filepath, sheet_name=active_sheet_name)
    elif extension == "csv":
        with _decode(open(filepath, "rb")) as f:
            result = read_csv(f)
        return result
    else:
        raise ValueError("Unrecognized file extension", extension)


def read_input_file(url, data: BinaryIO):
    """
    Download input data from the given URL to the given file-like object

    :param url: The source from which to download the data
    :param data: The destination to which to write the data
    """
    if url.startswith("file://"):
        filepath = url[7:]
        with open(filepath, "rb") as f:
            while chunk := f.read(4096):
                data.write(chunk)
    elif url.startswith("http://") or url.startswith("https://"):
        with requests.get(url, stream=True) as f:
            for chunk in f.iter_content(4096):
                data.write(chunk)
    else:
        raise ValueError(f"unrecognized protocol: {url}")


def write_output_file(url, data: BinaryIO):
    """
    Uploads output data from the given file-like object to the given URL

    :param url: The destination to which to upload data
    :param data: The source from which to read the data
    """
    if url.startswith("file://"):
        filepath = url[7:]
        with open(filepath, "wb") as f:
            while chunk := data.read(4096):
                f.write(chunk)
    elif url.startswith("http://") or url.startswith("https://"):
        requests.put(url, data=data)
    else:
        raise ValueError(f"unrecognized protocol: {url}")
