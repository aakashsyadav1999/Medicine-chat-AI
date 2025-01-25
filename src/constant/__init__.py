import os
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TIMESTAMP: str = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

ARTIFACTS_DIR = os.path.join("artifacts")
LOGS_DIR = "logs"
LOGS_FILE_NAME = "SIDFC.log"

# LLM Model API KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# LLM Model Name
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")
