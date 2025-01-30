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
from openai import OpenAI
import openai
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


# OpenAI Chat API Configuration
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    def llm_call(self):
        try:
            image_path = r"D:\vscode\Medicine-chat-AI\photos\20250127_194229.jpg"
            encoded_image = self.encode_image(image_path)

            if not encoded_image:
                logging.error("Encoded image is empty")
                return

            logging.info(f"Encoded image first 50 characters: {encoded_image[:50]}...")

            model = self.model.model()
            prompt_text = self.prompt.prompt_main()

            if not isinstance(prompt_text, str):
                logging.error("Prompt text is invalid")
                return

            # Initialize memory for conversation context
            conversation_memory = [{"role": "user", "content": prompt_text}]

            content_parts = [
                {'text': prompt_text},
                {'inline_data': {'mime_type': 'image/jpeg', 'data': encoded_image}}
            ]

            generate_request = {
                'contents': [{'parts': content_parts}],
                'stream': True,
                'safety_settings': [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ],
                'generation_config': {
                    "response_mime_type": "application/json"
                }
            }

            # Generate response from LLM
            response = model.generate_content(**generate_request)
            response.resolve()

            raw_response = response.text

            # Debug: Print Raw Response
            print("RAW RESPONSE:", raw_response)

            try:
                final_response_json = json.loads(raw_response)
                print("Initial Response:", json.dumps(final_response_json, indent=4))

                # Add response to conversation memory
                conversation_memory.append({"role": "assistant", "content": final_response_json})
                logging.info(f"Final response: {json.dumps(final_response_json, indent=4)}")

                # Check if the LLM advises using a tool
                call_agent_flag = final_response_json.get("use_tool", False)
                search_query = final_response_json.get("search_query", None)

                if call_agent_flag and search_query:
                    print(f"LLM suggested calling agent for query: {search_query}")
                    agent_message = {"role": "assistant", "content": {"parts": [{"text": search_query}]}}
                    self.agent.agent_call(agent_message)
                    print("Agent response complete.\n")

                # Initialize conversation memory
                conversation_memory = [{"role": "system", "content": "You are a helpful assistant."}]

               # START Follow-up Question Loop
                while True:
                    follow_up_question = input("Enter your follow-up question (or 'exit' to quit): ")
                    if follow_up_question.lower() == 'exit':
                        break

                    # Append user's question to conversation history
                    conversation_memory.append({"role": "user", "content": follow_up_question})

                    try:
                        # Generate response using OpenAI Chat API (New format)
                        response = client.chat.completions.create(
                            model="gpt-4",  # or "gpt-3.5-turbo"
                            messages=conversation_memory,
                            temperature=0.7,
                        )

                        raw_response = response.choices[0].message.content

                        try:
                            follow_up_response = json.loads(raw_response)  # Attempt JSON parsing
                        except json.JSONDecodeError:
                            follow_up_response = {"answer": raw_response}  # Treat raw response as answer

                        answer = follow_up_response.get("answer")
                        if answer:
                            print(f"Follow-up Answer: {answer}")
                        else:
                            print(f"Follow-up Response: {follow_up_response}")

                        # ✅ Save raw response in memory
                        conversation_memory.append({"role": "assistant", "content": raw_response})

                        # Handling Agent Calls (if necessary)
                        call_agent_flag = follow_up_response.get("use_tool", False)
                        search_query = follow_up_response.get("search_query", None)

                        if call_agent_flag and search_query:
                            print(f"Calling agent for follow-up search: {search_query}")
                            agent_message = {"role": "assistant", "content": [{"text": search_query}]}

                            if search_query.strip():
                                self.agent.agent_call(agent_message)

                    except openai.APIError as e:  # Corrected error handling for new API
                        logging.error(f"OpenAI API Error: {e}")
                        print(f"OpenAI API Error: {e}")

            except json.JSONDecodeError:
                logging.error("Error parsing initial response as JSON.")
                print(f"Raw response: {raw_response}")

        except Exception as e:
            logging.error(f"Unexpected error in API call: {e}")
            print(f"ERROR: {e}")



if __name__ == '__main__':
    main_script = MainScript()
    main_script.run()
    main_script.llm_call()
