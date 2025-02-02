# Medicine Chat AI

Medicine Chat AI is a Streamlit-based application designed to assist with medicine-related queries. The application leverages OpenAI's language model to provide intelligent responses and can analyze images uploaded by the user.

## Features

- **Interactive Chat Interface**: Engage in a conversation with the AI bot to get answers to your medicine-related questions.
- **Image Analysis**: Upload images for analysis and receive relevant information.
- **Session Management**: Maintains conversation history for a seamless user experience.

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/Medicine-chat-AI.git
    cd Medicine-chat-AI
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    - Create a `.env` file in the root directory.
    - Add your OpenAI API key:
      ```
      OPENAI_API_KEY=your_openai_api_key
      ```

## Usage

1. **Run the Streamlit application**:
    ```bash
    streamlit run app.py
    ```

2. **Interact with the bot**:
    - Type your query in the text area.
    - Optionally, upload an image for analysis.
    - Click the "Send" button to receive a response from the AI.

## Project Structure

- `app.py`: The main entry point for the Streamlit application.
![Medical Chat UI](documents-photos\app_interface.png)
![Medical Chat UI INFO](documents-photos\app_button_info.png)
- `src/components/main_script.py`: Contains the `MainScript` class which handles the core functionalities such as image encoding and API calls.
- `src/components/models.py`: Defines the models used in the application.
- `src/prompts/prompts.py`: Contains the prompt templates used for generating responses.
- `src/logger.py`: Configures logging for the application.
- `src/exception.py`: Custom exception handling.
- `src/components/database.py`: Handles database interactions.
- `src/components/agents.py`: Defines the agent used for interacting with the OpenAI API.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [OpenAI](https://openai.com/)
- [Pillow](https://python-pillow.org/)
