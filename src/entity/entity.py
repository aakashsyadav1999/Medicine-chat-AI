from src.constant import *
from dataclasses import dataclass


@dataclass
class LLMModel:

    def __init__(self):

        self.original_api_key = GEMINI_API_KEY
        self.model_name = GEMINI_MODEL_NAME
