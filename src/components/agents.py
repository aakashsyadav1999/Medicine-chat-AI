from phi.agent import Agent
from phi.tools.duckduckgo import DuckDuckGo
from phi.model.openai import OpenAIChat
import os
from dotenv import load_dotenv, find_dotenv
import logging


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

    def agent_call(self, data):
        try:
            # Extract the text content from parts if present
            if isinstance(data, dict) and "content" in data and "parts" in data["content"]:
                parts_content = " ".join(part.get("text", "") for part in data["content"]["parts"])
            else:
                parts_content = str(data)

            # Create structured agent input
            agent_data = {
                "role": "user",  # Pass as user input to the agent
                "content": parts_content.strip()
            }

            agent = Agent(
                model=OpenAIChat(id="gpt-4o"),
                api_key=os.getenv("OPENAI_API_KEY"),
                tools=[DuckDuckGo()],
                description=(
                    "You are a medicine expert and you tell why a doctor has prescribed a particular medicine."
                ),
                instructions=[
                    """Please analyze the attached photo of the medicine. Provide the advantages and disadvantages, and explain why a doctor
                    might prescribe it. Ensure your response is strictly limited to medical terms."""
                ],
                markdown=True,
                show_tool_calls=True,
                add_datetime_to_instructions=True,
            )

            # Call agent with properly formatted data
            agent.print_response(agent_data, stream=False)

        except Exception as e:
            logging.error(f"Error in agent_call: {e}")
