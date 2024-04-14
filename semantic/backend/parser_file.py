import io
from striprtf.striprtf import rtf_to_text
from PyPDF2 import PdfReader
import pandas as pd
import docx2txt


class ParserFile:
    """
    Parser for binary files
    """

    @staticmethod
    def read_txt(file) -> str:
        contents = file.file.read()
        return contents.decode('utf-8')

    @staticmethod
    def read_rtf(file) -> str:
        contents = file.file.read()
        text_rtf = contents.decode('UTF-8')
        extracted_text = rtf_to_text(text_rtf)
        return extracted_text

    @staticmethod
    def read_pdf(file) -> str:
        contents = file.file.read()
        pdf_reader = PdfReader(io.BytesIO(contents))
        extracted_text = ''
        for page in pdf_reader.pages:
            extracted_text += page.extract_text()
        return extracted_text

    @staticmethod
    def read_xlsx(file) -> str:
        contents = file.file.read()
        extracted_text = pd.read_excel(
            io.BytesIO(contents)
        ).fillna(" ").to_string()
        # print(extracted_text)
        return extracted_text

    @staticmethod
    def read_docx(file) -> str:
        contents = file.file.read()
        extracted_text = docx2txt.process(
            io.BytesIO(contents)
        )
        return extracted_text


class ParserZip:
    """
    Parser for zip file
    """

    @staticmethod
    def read_txt(file_path: str) -> str:
        with open(file_path, encoding='utf-8') as file:
            contents = file.read()
        return contents

    @staticmethod
    def read_rtf(file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            contents = file.read()
        contents = rtf_to_text(contents)
        return contents

    @staticmethod
    def read_pdf(file_path: str) -> str:
        pdf_reader = PdfReader(file_path)
        extracted_text = ''
        for page in pdf_reader.pages:
            extracted_text += page.extract_text()
        return extracted_text

    @staticmethod
    def read_xlsx(file_path: str) -> str:
        extracted_text = pd.read_excel(file_path).fillna(" ").to_string()
        return extracted_text

    @staticmethod
    def read_docx(file_path: str) -> str:
        extracted_text = docx2txt.process(file_path)
        return extracted_text
