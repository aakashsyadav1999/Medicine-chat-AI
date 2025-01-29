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
from src.components.database import Database
from src.components.agents import MyAgent




class MainScript:

    def __init__(self):
        self.logging = logging
        self.logging.info('MainScript object created')
        self.model = Model()
        self.prompt = Prompt()
        self.agent = MyAgent()

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


    # Function to decode the image
    def llm_call(self, call_agent=True):
        try:
            # Path to the image
            image_path = r"D:\vscode\Medicine-chat-AI\photos\20250127_194229.jpg"
            # Prepare the image
            encoded_image = self.encode_image(image_path)

            if not encoded_image:
                logging.error("Encoded image is empty")
                return

            logging.info(f"Encoded image first 50 characters: {encoded_image[:50]}...")

            # Prepare model and content
            model = self.model.model()
            prompt_text = self.prompt.prompt_main()

            if not isinstance(prompt_text, str):
                logging.error("Prompt text is invalid")
                return

            content_parts = [{'text': prompt_text}, {'inline_data': {'mime_type': 'image/jpeg', 'data': encoded_image}}]

            if not content_parts:
                logging.error("Content parts list is empty or invalid")
                return

            # Generate initial response
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

            response = model.generate_content(
                **generate_request, generation_config={"response_mime_type": "application/json"}
            )
            response.resolve()
            raw_response = response.text

            try:
                final_response_json = json.loads(raw_response)
                print("Initial Response:", final_response_json)
                logging.info(f"Final response: {json.dumps(final_response_json, indent=4)}")
            except json.JSONDecodeError:
                logging.error("Error parsing initial response as JSON.")
                print(f"Raw response: {raw_response}")
                return

            # If agent is enabled, call the agent after initial output
            if call_agent:
                print("Calling agent...")
                agent_message = {
                    "role": "assistant",
                    "content": {"parts": [{"text": json.dumps(final_response_json)}]}
                }
                self.agent.agent_call(agent_message)
                return  # Exit after agent call

            # Follow-up questions loop
            previous_response = json.dumps(final_response_json)

            while True:
                follow_up_question = input("Enter your follow-up question (or 'exit' to quit): ")
                if follow_up_question.lower() == 'exit':
                    break

                # Maintain context by combining previous response and the new question
                context_text = f"Previously discussed: {previous_response}. Follow-up question: {follow_up_question}"

                content_parts = [{"text": context_text}]
                generate_request['contents'] = [{'parts': content_parts}]

                try:
                    response = model.generate_content(
                        **generate_request, generation_config={"response_mime_type": "application/json"}
                    )
                    response.resolve()
                    raw_response = response.text

                    try:
                        final_response_json = json.loads(raw_response)
                        print("Follow-up Response:", final_response_json)
                        logging.info(f"Follow-up response: {json.dumps(final_response_json, indent=4)}")
                    except json.JSONDecodeError:
                        logging.error("Error parsing follow-up response as JSON.")
                        print(f"Raw follow-up response: {raw_response}")
                        continue

                    previous_response = json.dumps(final_response_json)

                except Exception as e:
                    logging.error(f"Unexpected error in follow-up API call: {e}")

        except Exception as e:
            logging.error(f"Unexpected error in API call: {e}")


if __name__ == '__main__':
    main_script = MainScript()
    main_script.run()
    main_script.llm_call()
