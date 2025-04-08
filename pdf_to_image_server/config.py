
import os
from pathlib import Path
from dotenv import load_dotenv
from pdf_to_image_server.log_init import logger

# Load environment variables
load_dotenv()

def create_if_not_exists(path: Path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

class Config:
    # Set default values if environment variables are not found
    temp_file_path = Path(os.getenv('TEMP_FILE_PATH', '/tmp/pdf_to_image_server'))
    create_if_not_exists(temp_file_path)
    
    max_upload_MB = int(os.getenv('MAX_UPLOAD_MB', '100'))
    max_message_size = max_upload_MB * 1024 * 1024
    fast_api_port = int(os.getenv('FAST_API_PORT', '8000'))
    remote_server = os.getenv('REMOTE_SERVER', 'http://localhost:8000')
    
    doc_location = Path(os.getenv('DOC_LOCATION', '/tmp'))
    create_if_not_exists(doc_location)
    
    cache_folder = Path(os.getenv('CACHE_FOLDER', '/tmp/pdf_to_image_server/cache'))
    create_if_not_exists(cache_folder)
    
    target_css_folder = Path(os.getenv('TARGET_CSS_FOLDER', '/tmp/pdf_to_image_server/css'))
    create_if_not_exists(target_css_folder)

cfg = Config()    
if __name__ == "__main__":
    logger.info(os.getenv('DOC_LOCATION'))
    logger.info(cfg.fast_api_port)
