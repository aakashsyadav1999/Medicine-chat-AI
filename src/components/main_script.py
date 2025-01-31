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
            image_path = r"D:\\vscode\\Medicine-chat-AI\\photos\\20250127_194229.jpg"
            encoded_image = self.encode_image(image_path)

            if not encoded_image:
                logging.error("Encoded image is empty")
                return

            logging.info(f"Encoded image first 50 characters: {encoded_image[:50]}...")

            prompt_text = self.prompt.prompt_main()

            if not isinstance(prompt_text, str):
                logging.error("Prompt text is invalid")
                return

            conversation_memory = self.initialize_conversation_memory(prompt_text)
            content_parts = self.build_content_parts(prompt_text, encoded_image)
            generate_request = self.build_generate_request(content_parts)

            raw_response = self.generate_llm_response(generate_request)
            if not raw_response:
                return

            final_response_json = self.parse_response(raw_response)
            if final_response_json is None:
                return

            self.handle_initial_response(final_response_json, conversation_memory)
            self.handle_follow_up_questions(conversation_memory)

        except Exception as e:
            logging.error(f"Unexpected error in API call: {e}")
            print(f"ERROR: {e}")

    def initialize_conversation_memory(self, prompt_text):
        return [{"role": "user", "content": prompt_text}]

    def build_content_parts(self, prompt_text, encoded_image):
        return [
            {'text': prompt_text},
            {'inline_data': {'mime_type': 'image/jpeg', 'data': encoded_image}}
        ]

    def build_generate_request(self, content_parts):
        return {
            'contents': [{'parts': content_parts}],
            'stream': True,
            'safety_settings': [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ],
            'generation_config': {"response_mime_type": "application/json"}
        }

    def generate_llm_response(self, generate_request):
        try:
            model = self.model.model()
            response = model.generate_content(**generate_request)
            response.resolve()
            return response.text
        except Exception as e:
            logging.error(f"Error during LLM response generation: {e}")
            return None

    def parse_response(self, raw_response):
        try:
            final_response_json = json.loads(raw_response)
            print("Initial Response:", json.dumps(final_response_json, indent=4))
            return final_response_json
        except json.JSONDecodeError:
            logging.error("Error parsing initial response as JSON.")
            print(f"Raw response: {raw_response}")
            return None

    def handle_initial_response(self, final_response_json, conversation_memory):
        # Append the assistant's response to the conversation memory
        conversation_memory.append({"role": "assistant", "content": json.dumps(final_response_json)})

        call_agent_flag = final_response_json.get("use_tool", False)

        if call_agent_flag:
            print("LLM suggested calling agent for further information.")

            # Extract the medicine name or default to a generic query
            medicine_name = final_response_json.get("proper_name", "general query")
            agent_message = {"role": "assistant", "content": medicine_name}

            # Trigger the agent for initial query
            self.agent.agent_call(agent_message)
            print("Agent response complete.\n")

            # Handle follow-up questions via agent
            while True:
                follow_up_question = input("Enter your follow-up question (or 'exit' to quit): ")
                if follow_up_question.lower() == 'exit':
                    break

                # Redirect follow-up to agent instead of LLM
                follow_up_agent_message = {"role": "assistant", "content": follow_up_question}
                self.agent.agent_call(follow_up_agent_message)
                print("Agent response complete.\n")

    def handle_follow_up_questions(self, conversation_memory):
        conversation_memory.append({"role": "system", "content": "You are a helpful assistant."})
        while True:
            follow_up_question = input("Enter your follow-up question (or 'exit' to quit): ")
            if follow_up_question.lower() == 'exit':
                break

            conversation_memory.append({"role": "user", "content": follow_up_question})
            self.process_follow_up(conversation_memory)

    def process_follow_up(self, conversation_memory):
        try:
            for message in conversation_memory:
                if not isinstance(message.get("content"), str):
                    message["content"] = json.dumps(message["content"])

            response = client.chat.completions.create(
                messages=conversation_memory,
                temperature=0.4,
                model="gpt-4o-mini",
            )

            raw_response = response.choices[0].message.content.strip()
            print(f"Follow-up Answer: {raw_response}")

            # Append assistant response to conversation
            conversation_memory.append({"role": "assistant", "content": raw_response})

            # Detect if user asks for Google search
            if "search Google" in raw_response.lower() or "find information" in raw_response.lower():
                print("Triggering agent search...")
                search_query = input("Enter your search query: ")
                if search_query.strip():
                    agent_message = {"role": "assistant", "content": search_query}
                    self.agent.agent_call(agent_message)

        except Exception as e:
            logging.error(f"OpenAI API Error: {e}")
            print(f"OpenAI API Error: {e}")



if __name__ == '__main__':
    main_script = MainScript()
    main_script.run()
    main_script.llm_call()
