import google.generativeai as genai
import re
import sys
import os

# Add the project root to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.logger import logging
from src.exception import CustomException
from src.entity.entity import LLMModel

class Model:

    def __init__(self):
        self.logger = logging
        self.logger.info('Model object created')
        self.llm_model = LLMModel()

    def model(self):
        try:
            #define api key
            self.api_key = self.llm_model.original_api_key
            #configure api key
            genai.configure(api_key=self.api_key)
            #Define which model we are going to use
            gemini_model = genai.GenerativeModel(self.llm_model.model_name)
            logging.info(f"Gemini model configured: {gemini_model}")
            #return model
            return gemini_model
        except Exception as e:
            logging.error(f"Failed to configure Gemini API: {e}")
            CustomException(e,sys)

    def generate_text(self, model, prompt):
        try:
            #generate text
            generated_text = model.generate_text(prompt)
            logging.info(f"Generated text: {generated_text}")
            return generated_text
        except Exception as e:
            logging.error(f"Failed to generate text: {e}")
            CustomException(e,sys)

    def generate_image(self, model, prompt):
        try:
            #generate image
            generated_image = model.generate_image(prompt)
            logging.info(f"Generated image: {generated_image}")
            return generated_image
        except Exception as e:
            logging.error(f"Failed to generate image: {e}")
            CustomException(e,sys)

