# AI Chat Interface

A modern, desktop chat application for interacting with locally hosted LLMs with Ollama. Features a clean interface with syntax highlighting, mermaid diagram support, and conversation history management.

Its a fun project for interacting with LLMs locally. 
My setup is with WSL2 on Windows 11 and Ollama installed in Windows.
I have the docker container running in WSL2.
Although I'm sure there are some bugs and issues, I'm still working on it.

Note that I've added a dev container to make it easier to run the application, but it doesn't seem to work with the current version.

## Features

- 🎨 Modern dark theme UI with syntax highlighting
- 📊 Built-in mermaid diagram rendering
- 💾 Conversation history saving
- 📝 Markdown formatting support
- 🖥️ Console output panel for debugging
- 🎯 Multi-model support

## Screenshots

Working screenshots with Deepseek running locally.

![Screenshot 1](./docs/screenshot1.png)
![Screenshot 2](./docs/screenshot2.png)
![Screenshot 3](./docs/screenshot3.png)
![Screenshot 4](./docs/screenshot4.png)
![Screenshot 5](./docs/screenshot5.png)

## Demo

![Demo GIF](./docs/demo.gif)

Sorry for the super low resolution gif, can't make a 4k one with any free software on Windows, let me know if there is any good ones!

# End Generation Here


## Installation

### Development Setup

1. Clone the repository

    ```bash
    git clone git@github.com:zmcddn/llm_gui.git
    cd llm_gui
    ```

2. Run the application:

    ```bash
    make up
    ```

### Running Tests

```bash
make test
```

## Usage

1. Launch the application
2. Select your preferred AI model from the settings
    - You can use any model that Ollama supports
    - I'm using llama3.1:32b
3. Type your message in the input box
4. Click Send to get a response
5. Use the Save Conversation button to export chat history
    - This will save the chat history to the `conversations` folder

## Project Structure

```
llm_gui/
├── gui.py               # Main GUI implementation
├── llm.py               # LLM integration and response formatting
├── styles.py            # UI styling and theme definitions
├── templates.py         # HTML templates for output
├── tests/               # Test suite
├── conversations/       # Saved chat histories
├── Makefile             # Build and run commands
└── requirements.txt     # Python dependencies
```

## Dependencies

- Python 3.8+
- PyQt6
- Pygments
- Markdown

## License

MIT-licensed
