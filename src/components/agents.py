from phi.agent import Agent
from phi.tools.duckduckgo import DuckDuckGo
from phi.model.openai import OpenAIChat
import os
from dotenv import load_dotenv, find_dotenv
import logging
import requests

# Load environment variables
load_dotenv(find_dotenv())
class MyAgent(Agent):
    """MyAgent class to handle the agent operations."""

    # Initialize the agent
    def __init__(self):
        """Initialize the agent."""
        super().__init__()
        self.duck = DuckDuckGo()
        self.data = None

    # Define the step method
    def step(self, dt):
        """Step the agent."""
        self.data = self.duck.search('Pinecone AI')
        return self.data

    # Define the reset method
    def reset(self):
        """Reset the agent."""
        self.data = None
        return self.data

    # Define the get_data method
    def get_response(self, query):
        """Get the response from the DuckDuckGo API."""
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json"}
        )

        if response.status_code == 200:
            return response.json()  # Return structured response instead of printing
        else:
            return {"error": "Failed to fetch response"}

    # Define the handle_request method
    def handle_request(self, query):
        """Handle the request and print the response."""
        response = self.get_response(query)
        print("Response from agent:", response)

    # Define the agent_call method
    def agent_call(self, data):
        """Call the agent with the given data and return the response."""
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
            response = agent.run(agent_data)  # Use run method processes the input and returns the agent's response without printing it.
            logging.info(f"Agent response: {response.content}")

            if response.content:
                return response.content  # Return instead of printing
            else:
                logging.error("Agent response is empty or None.")
                return None

        except Exception as e:
            logging.error(f"Error in agent_call: {e}")
            return None
