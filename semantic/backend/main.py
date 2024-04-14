import os
import shutil
import json
import shutil

import pandas as pd
import aiofiles
import zipfile
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .model import SemanticModel
from .parser_file import ParserFile, ParserZip
from fastapi.responses import FileResponse

model_ = SemanticModel()
parser = ParserFile()
parser_zip = ParserZip()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

mapping = {
    "proxy": "Доверенность",
    "contract": "Договор",
    "act": "Акт",
    "application": "Заявление",
    "order": "Приказ",
    "invoice": "Счет",
    "bill": "Приложение",
    "arrangement": "Соглашение",
    "contract offer": "Договор оферты",
    "statute": "Устав",
    "determination": "Решение",
    "no_class": "Без классификации"
}


@app.get("/form_params")
async def read_json_file():
    try:
        json_file_path = os.path.join(os.path.dirname(__file__), "/app/data.json")
        with open(json_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return JSONResponse(content=data)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")


@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...), doctype: str = Form(...)):
    resp = {"files": {}}
    data = {'filename': [], 'text': []}
    read_config = {".txt": parser.read_txt,
                   ".rtf": parser.read_rtf,
                   ".pdf": parser.read_pdf,
                   ".xlsx": parser.read_xlsx,
                   ".docx": parser.read_docx,
                   }
    # try:
    for file in files:
        contents = read_config[os.path.splitext(file.filename)[1]](file)
        data["filename"].append(file.filename)
        data["text"].append(contents)

    # Parse json
    json_file_path = os.path.join(os.path.dirname(__file__), "/app/data.json")
    with open(json_file_path, "r", encoding="utf-8") as file:
        json_file = json.load(file)
    cats = json_file[doctype]['categories']
    cats = {cat: 1 for cat in cats}

    df_data = pd.DataFrame(data)
    res_data = model_.predict(df_data)

    total_status = True
    for filename, category in res_data.items():
        if category not in cats:
            resp["files"][filename] = {
                "category": mapping[category],
                "valid_type": f"Неожиданная категория, ожидалась категория из списка: "
                              f"[{', '.join([mapping[i] for i in cats.keys()])}]",
            }
            total_status = False
        elif cats[category] == 1:
            resp["files"][filename] = {
                "category": mapping[category],
                "valid_type": "Правильный документ",
            }
            cats[category] -= 1
        else:
            resp["files"][filename] = {
                "category": mapping[category],
                "valid_type": "Лишний документ",
            }
            total_status = False

    # resp : {'files': {'1.txt': {'category': 'application'}}}

    if total_status is True:
        resp["status"] = "ok"
    else:
        resp["status"] = "bad"

    return JSONResponse(content=resp, status_code=200)
    # except Exception as e:
    #     print(e)
    #     return JSONResponse(content={"message": "Failed to upload files", "error": str(e)}, status_code=500)


@app.post("/handle_example")
async def handle_example(request: dict):
    if "name" not in request:
        return JSONResponse(content={"message": "Failed to upload files", "error": "wrong format"}, status_code=500)
    name = request["name"]
    if name == "first":

        res = {'files': {
            'soglasie.rtf':
                {'category': mapping['arrangement'], "valid_type": "Правильный документ"},
            'bill.rtf':
                {'category': mapping['bill'], "valid_type": "Правильный документ"},
            'bill_another.rtf':
                {'category': mapping['bill'], "valid_type": "Лишний документ"}
        },
            'status': 'bad'
        }
    elif name == "second":
        res = {'files': {
            'soglasie.rtf':
                {'category': mapping['arrangement'], "valid_type": "Правильный документ"},
            'bill.rtf':
                {'category': mapping['bill'], "valid_type": "Правильный документ"},
            'order.rtf':
                {'category': mapping['order'], "valid_type": "Правильный документ"}
        },
            'status': 'ok'
        }
    else:
        return JSONResponse(content={"message": "Failed to upload files", "error": "wrong format"}, status_code=500)

    return JSONResponse(content=res, status_code=200)

def read_doc_zip(paths: list[str]) -> dict:
    data = {'filename': [], 'text': []}
    read_config = {".txt": parser_zip.read_txt,
                   ".rtf": parser_zip.read_rtf,
                   ".pdf": parser_zip.read_pdf,
                   ".xlsx": parser_zip.read_xlsx,
                   ".docx": parser_zip.read_docx,
                   }

    for path in paths:
        contents = read_config[os.path.splitext(path)[1]](path)
        data["filename"].append(path)
        data["text"].append(contents)
    preds = model_.predict(pd.DataFrame(data))
    return preds


def create_folders_and_sort_files(folders_dict, folder_name):
    for filename, prediction_classname in folders_dict.items():
        if not os.path.exists(folder_name + f"/{prediction_classname}/"):
            os.mkdir(folder_name + prediction_classname)
            destination_path = os.path.join(folder_name + f"/{prediction_classname}/", os.path.basename(filename))
            shutil.copy(filename, destination_path)


def create_zip_response(dir_name):
    """
    Создает ZIP-архив из папки, включая все файлы внутри.

    :param folder_path: Путь к папке, которую нужно запаковать.
    :param output_zip_path: Путь к выходному ZIP-файлу.
    """
    try:
        if os.path.exists("/app/tmp/result.zip"):
            os.remove("/app/tmp/result.zip")

        with zipfile.ZipFile('/app/tmp/result.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk('/app/tmp'):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Добавляем файл в архив с сохранением относительной структуры папок
                    zipf.write(file_path, os.path.relpath('/app/tmp/', '/app/tmp'))
        print(f"Папка успешно запакована в /app/tmp/")
    except Exception as e:
        print(f"Ошибка при создании ZIP-архива: {e}")
    return FileResponse(r'/app/tmp/result.zip')

@app.post("/upload_zip")
async def upload_zip(file: UploadFile = File(...)):
    async with aiofiles.open(f'/app/tmp/{file.filename}', 'wb') as out_file:
        while content := await file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk

    archive_name = os.path.splitext(file.filename)[0]

    os.mkdir(f"/app/tmp/{archive_name}")
    with zipfile.ZipFile(f'/app/tmp/{file.filename}') as raw_zipfile:
        raw_zipfile.extractall(path=f"/app/tmp/{archive_name}")

    filenames = []
    for filename in os.listdir(f"/app/tmp/{archive_name}"):
        filenames.append(f"/app/tmp/{archive_name}/" + filename)

    path_to_mapping = read_doc_zip(filenames)
    create_folders_and_sort_files(path_to_mapping, f"/app/tmp/{archive_name}/")
    response = create_zip_response(archive_name)  # FUNCTION TO CREATE RESPONSE

    try:
        os.remove(f"/app/tmp/{file.filename}")
        shutil.rmtree(f"/app/tmp/{archive_name}")
    except (FileNotFoundError, ):
        pass
    return response

# @app.post("/upload_zip")
# async def upload_zip(file: UploadFile = File(...)):
#     if not file.filename.endswith(".zip"):
#         raise HTTPException(status_code=400, detail="Uploaded file must be a .zip file")
#
#     file_path = os.path.join("/app", file.filename)
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#
#     return FileResponse(file_path)

@app.post("/update_template")
async def update_template(request: dict):
    try:
        json_file_path = os.path.join("/app/data.json")
        with open(json_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if len(request['categories']) == 0:
            return JSONResponse(status_code=200, content={'error': "No categories have been chosen!"})

        new_key = 'custom_key_'
        numeric_ending = 0
        for key in data:
            if request['name'] == data[key]["name"]:
                return JSONResponse(status_code=200, content={'error': f"Name {request['name']} already exists!"})

            if new_key + str(numeric_ending) in data:
                numeric_ending += 1

        new_key = 'custom_key_' + str(numeric_ending)

        new_value = {
            'name': request['name'],
            'categories': request['categories'],
            'docs_number': len(request['categories'])
        }
        data[new_key] = new_value
        with open(json_file_path, "w", encoding="utf-8") as file:
            json.dump(data, file)
        return JSONResponse(content=data, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail={'error': str(e)})