from pathlib import Path
import os
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi import File, UploadFile

from pdf_to_image_server.config import cfg
from pdf_to_image_server.log_init import logger
from pdf_to_image_server.caching import read_file, write_file

from pdf_ocr.pdf_image_ocr.image_ocr import convert_img_to_text

import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CODE_OK = 'OK'
CODE_FAIL = 'FAIL'


def message_factory(file_name: str, contents: str, code: str) -> dict:
    return {
        "code": code,
        "message": f"Successfully uploaded {file_name}",
        "extracted_text": contents,  # ensure this key matches
        "status": "success"
    }


@app.post("/upload")
def upload(file: UploadFile = File(...)):
    try:
        cached_contents = read_file(file.filename)
        if cached_contents is not None:
            return message_factory(file.filename, cached_contents, CODE_OK)
        
        contents = file.file.read()
        logger.info("Upload received")
        tmp_path = cfg.temp_file_path
        file_path: Path = tmp_path/file.filename
        
        with open(file_path, 'wb') as f:
            f.write(contents)
            
        extracted_text = convert_img_to_text(file_path)
        if extracted_text:
            write_file(content=extracted_text, file_name=file.filename)
            return message_factory(file.filename, extracted_text, CODE_OK)
        else:
            return {
                'code': CODE_FAIL,
                'message': "Failed to extract text from PDF",
                'extracted_text': ""
            }
            
    except Exception as e:
        logger.exception("An error occurred during file upload")
        return {
            'code': CODE_FAIL,
            'message': f"Error processing file: {str(e)}",
            'extracted_text': ""
        }
    finally:
        try:
            file.file.close()
        except:
            pass



@app.post("/upload_styles")
def upload(file: UploadFile = File(...)):
    contents = file.file.read()
    target_css_folder = cfg.target_css_folder
    target_file = target_css_folder/'onepoint.css'
    with open(target_file, 'wb') as f:
        f.write(contents)
    return {
        'code': CODE_OK
    }


@app.get("/cached_file/{file_name}")
async def read_item(file_name: str):
    cached_contents = read_file(file_name)
    if cached_contents is not None:
        return message_factory(file_name, cached_contents, CODE_OK)
    return message_factory(file_name, "", CODE_FAIL)


@app.get("/")
def read_root():
    return {"Hello": "PDF to Image Server"}

if __name__ == '__main__':
    logger.info("Fast API server starting on port: %s", cfg.fast_api_port)    
    uvicorn.run(app, port=cfg.fast_api_port)
