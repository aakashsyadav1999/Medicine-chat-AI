from phi.agent import Agent
from phi.tools.duckduckgo import DuckDuckGo
from phi.model.openai import OpenAIChat
import os
from dotenv import load_dotenv, find_dotenv
import logging
import requests


class MyAgent(Agent):

    def __init__(self):
        super().__init__()
        self.duck = DuckDuckGo()
        self.data = None

    def step(self, dt):
        self.data = self.duck.search('Pinecone AI')
        return self.data

    def reset(self):
        self.data = None
        return self.data

    def get_response(self, query):
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json"}
        )

        if response.status_code == 200:
            return response.json()  # Return structured response instead of printing
        else:
            return {"error": "Failed to fetch response"}

    def handle_request(self, query):
        response = self.get_response(query)
        print("Response from agent:", response)


    def agent_call(self, data):
        try:
            # Extract text from data or handle as a simple string
            parts_content = (
                " ".join(part.get("text", "") for part in data["content"]["parts"])
                if isinstance(data, dict) and "content" in data and "parts" in data["content"]
                else str(data)
            )

            # Prepare agent data
            agent_data = {
                "role": "user",
                "content": parts_content.strip()
            }

            # Create an agent instance
            agent = Agent(
                model=OpenAIChat(id="gpt-4o"),
                api_key=os.getenv("OPENAI_API_KEY"),
                tools=[DuckDuckGo()],
                description="You are a medicine expert and you tell why a doctor has prescribed a particular medicine.",
                instructions=["Analysis medicine and tell proper response."],
                markdown=True,
                show_tool_calls=True,
                add_datetime_to_instructions=True,
            )

            # Get and return the response directly
            response = agent.run(agent_data)  # Use get_response instead of print_response
            logging.info(f"Agent response: {response.content}")

            if response.content:
                return response.content  # Return instead of printing
            else:
                logging.error("Agent response is empty or None.")
                return None

        except Exception as e:
            logging.error(f"Error in agent_call: {e}")
            return None
