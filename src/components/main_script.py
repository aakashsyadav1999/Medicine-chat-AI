import os
import sys
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
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

# MainScript class
class MainScript:

    # Constructor
    def __init__(self):
        """Initialize the MainScript object."""
        self.logging = logging
        self.logging.info('MainScript object created')
        self.model = Model()
        self.prompt = Prompt()
        self.agent = MyAgent()

    # Run method
    def run(self):
        """Run the main script."""
        self.logging.info('Medicine-chat-AI method called')
        try:
            self.logging.info('Medicine-chat-AI method called')
            print('Medicine-chat-AI method called')
        except Exception as e:
            self.logging.error(f'Error in Medicine-chat-AI method called {e}')
            raise CustomException('Error Medicine-chat-AI method called', e)

    # Function to select photos
    def select_photos(self):
        """Select photos from the photos directory."""
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
        """Encode an image file to base64."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except FileNotFoundError as e:
            logging.error(f"Image file not found: {e}")


    # Function to decode the image
    def llm_call(self):
        """Call the LLM API with an image and prompt text."""
        try:
            # Image path
            image_path = r"D:\\vscode\\Medicine-chat-AI\\photos\\20250127_194229.jpg"
            encoded_image = self.encode_image(image_path)

            # Check if the encoded image is empty
            if not encoded_image:
                logging.error("Encoded image is empty")
                return

            logging.info(f"Encoded image first 50 characters: {encoded_image[:50]}...")

            # Prompt text
            prompt_text = self.prompt.prompt_main()
            # Check if the prompt text is valid
            if not isinstance(prompt_text, str):
                logging.error("Prompt text is invalid")
                return

            # Initialize conversation memory
            conversation_memory = self.initialize_conversation_memory(prompt_text)
            content_parts = self.build_content_parts(prompt_text, encoded_image)
            generate_request = self.build_generate_request(content_parts)
            # Generate response
            raw_response = self.generate_llm_response(generate_request)
            if not raw_response:
                return

            # Parse response
            final_response_json = self.parse_response(raw_response)
            if final_response_json is None:
                return

            # Handle initial response
            self.handle_initial_response(final_response_json, conversation_memory)
            # Handle follow-up questions
            self.handle_follow_up_questions(conversation_memory)

        except Exception as e:
            logging.error(f"Unexpected error in API call: {e}")
            print(f"ERROR: {e}")

    # Function to initialize conversation memory
    def initialize_conversation_memory(self, prompt_text):
        """Initialize the conversation memory for the LLM API."""
        return [{"role": "user", "content": prompt_text}]

    # Function to build content parts
    def build_content_parts(self, prompt_text, encoded_image):
        """Build the content parts for the LLM API."""
        return [
            {'text': prompt_text},
            {'inline_data': {'mime_type': 'image/jpeg', 'data': encoded_image}}
        ]

    # Function to build generate request
    def build_generate_request(self, content_parts):
        """Build the generate request for the LLM API."""
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
    # Function to generate LLM response
    def generate_llm_response(self, generate_request):
        """Generate a response from the LLM API."""
        try:
            model = self.model.model()
            response = model.generate_content(**generate_request)
            response.resolve()
            return response.text
        except Exception as e:
            logging.error(f"Error during LLM response generation: {e}")
            return None

    # Function to parse response
    def parse_response(self, raw_response):
        """Parse the response from the LLM API."""
        try:
            final_response_json = json.loads(raw_response)
            print("Initial Response:", json.dumps(final_response_json, indent=4))
            return final_response_json
        except json.JSONDecodeError:
            logging.error("Error parsing initial response as JSON.")
            print(f"Raw response: {raw_response}")
            return None

    # Function to handle follow-up questions
    def handle_follow_up_questions(self, conversation_memory):
        """Handle follow-up questions using LLM."""
        while True:
            follow_up_question = input("Enter your follow-up question (or 'exit' to quit): ")
            if follow_up_question.lower() == "exit":
                break

            conversation_memory.append({"role": "user", "content": follow_up_question})

            # Example condition for using tool
            use_tool = "web" in follow_up_question.lower() or "internet" in follow_up_question.lower()

            if use_tool:
                print("Triggering agent for follow-up question...")
                self.trigger_agent(follow_up_question, conversation_memory)
            else:
                self.process_follow_up(conversation_memory)

    # Function to handle initial response
    def handle_initial_response(self, final_response_json, conversation_memory):
        """Handle the initial response from the LLM API."""
        try:
            print("Handling Initial Response...")
            print("Initial Response:", json.dumps(final_response_json, indent=4))
            conversation_memory.append({"role": "assistant", "content": str(final_response_json)})
        except Exception as e:
            logging.error(f"Error handling initial response: {e}")
            print(f"Error handling initial respError during agent callonse: {e}")

    # Function to trigger agent
    def trigger_agent(self, query, conversation_memory):
        """Trigger the agent for follow-up questions."""
        try:
            # Append user query to memory
            conversation_memory.append({"role": "user", "content": query})

            # Pass full conversation memory to the agent
            response = self.agent.agent_call(conversation_memory)
            print("Agent response from main file:", response)

            # # Check if the response is None
            if response is None:
                print("Error: No response from agent.")
                logging.error("Error: No response from agent.")
                return

            # Safely get content from response (if it exists)
            agent_content = response
            # Check if agent_content is empty or None
            if not agent_content:
                print("Error: Agent response content is empty or None.")
                logging.error("Error: Agent response content is empty or None.")
                return

            print("Agent response:", agent_content)

            # Save the agent response back to memory
            conversation_memory.append({"role": "assistant", "content": agent_content})

        except Exception as e:
            print(f"Error during agent call: {e}")
            logging.error(f"Error during agent call: {e}")

    # Function to process follow-up questions
    def process_follow_up(self, conversation_memory):
        """Process follow-up questions using LLM."""
        try:
            # Get the last user query
            response = client.chat.completions.create(
                messages=conversation_memory,
                temperature=0.4,
                model="gpt-4o-mini",
                timeout=30
            )
            # Check if the response is valid
            if response.choices:
                raw_response = response.choices[0].message.content.strip()
                print(f"Follow-up Answer: {raw_response}")
                conversation_memory.append({"role": "assistant", "content": raw_response})
            else:
                print("No valid response received from LLM.")
        except Exception as e:
            print(f"Unexpected Error: {e}")


# Main method
if __name__ == '__main__':
    main_script = MainScript()
    main_script.run()
    main_script.llm_call()
