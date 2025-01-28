import os
import sys
import shutil
import PIL.Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import base64
# Add the project root to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.components.models import Model
from src.prompts.prompts import Prompt
from src.logger import logging
from src.exception import CustomException
import json




class MainScript:

    def __init__(self):
        self.logging = logging
        self.logging.info('MainScript object created')
        self.model = Model()
        self.prompt = Prompt()

    def run(self):
        self.logging.info('MainScript run method called')
        try:
            self.logging.info('MainScript run method called')
            print('MainScript run method called')
        except Exception as e:
            self.logging.error(f'Error in MainScript run method {e}')
            raise CustomException('Error in MainScript run method', e)

    def select_photos(self):
        self.logging.info('Selecting photos')
        try:
            photos = []
            for file in os.listdir('photos'):
                if file.endswith('.jpg') or file.endswith('.png'):
                    photos.append(file)
            return photos
        except Exception as e:
            self.logging.error(f'Error in selecting photos {e}')
            raise CustomException('Error in selecting photos', e)

    # Function to encode the image
    def encode_image(self,image_path):
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except FileNotFoundError as e:
            logging.error(f"Image file not found: {e}")


    def llm_call(self):
        try:
            # Path to the image
            image_path = r"D:\vscode\Medicine-chat-AI\photos\20250127_194229.jpg"  # Replace with actual image path
            # Prepare the image
            encoded_image = self.encode_image(image_path)
            # Check if the image is valid
            if not encoded_image:
                logging.error("Encoded image is empty")
                return

            # Log the first 50 characters of the encoded image for debugging
            logging.info(f"Encoded image first 50 characters: {encoded_image[:50]}...")
            # Prepare model and content
            model = self.model.model()  # Correct method call
            # Ensure prompt is a valid string
            prompt_text = self.prompt.prompt_main()  # Correct method call
            if not isinstance(prompt_text, str):
                logging.error("Prompt text is invalid")
                return

            content_parts = [
                {'text': prompt_text},
                {'inline_data': {'mime_type': 'image/jpeg', 'data': encoded_image}}
            ]
            # Verify content_parts before sending to the model
            if not content_parts or not isinstance(content_parts, list):
                logging.error("content_parts is not a valid list or is empty")
            # Generate response
            generate_request = {
                'contents': [{'parts': content_parts}],
                'stream': True,
                'safety_settings': [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]
            }
            # Call generate method
            response = model.generate_content(**generate_request, generation_config={"response_mime_type": "application/json"})
            response.resolve()
            #final_response
            final_response = response.text
            final_response_json = json.loads(final_response)
            logging.info(f"Final response: {json.dumps(final_response_json, indent=4)}")

        except ValueError as e:
            logging.error(f"Image processing error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error in API call: {e}")


if __name__ == '__main__':
    main_script = MainScript()
    main_script.run()
    main_script.llm_call()
