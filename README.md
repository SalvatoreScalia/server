# Repl-Nix-Server

This is a Python-based server project using WebSockets for real-time communication. The server is designed to handle various types of messages, including chat, notifications, and game commands, and manages game states across multiple clients.

## Project Structure

```
server/
│
├── pyproject.toml       # Project dependencies and configuration
├── poetry.lock          # Locked dependencies
├── README.md            # Project documentation (this file)
├── repl_nix_server/     # Main package directory
│   ├── __init__.py      # Marks this directory as a Python package
│   ├── classes.py       # Contains the GameStage class and other related classes
│   ├── controller.py    # Handles data persistence and related logic
│   ├── servidor.py      # Contains WebSocket server setup and message handling
│   └── main.py          # Entry point for the server
└── static/              # Static files (if any)
```

## Features

- **WebSocket Server**: Supports real-time communication with multiple clients.
- **Game State Management**: Handles game states, allowing commands such as save, restore, and start new games.
- **Chat and Notifications**: Manages and broadcasts chat messages and notifications to connected clients.
- **Data Persistence**: Saves and restores game states and user data.

## Installation

To install the project and its dependencies, follow these steps:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/repl-nix-server.git
   cd repl-nix-server
   ```

2. **Install dependencies using Poetry**:

   ```bash
   poetry install
   ```

3. **Activate the virtual environment**:

   ```bash
   poetry shell
   ```

## Usage

To start the server, you can run the `main.py` file. Make sure you're in the virtual environment.

```bash
python -m repl_nix_server.main
```

The server will initialize and start listening for WebSocket connections on `ws://127.0.0.1:3001`.

## Configuration

- **WebSocket Paths**:
  - `/chat`: Handles chat messages between clients.
  - `/notifications`: Sends notifications to all connected clients.
  - `/game`: Manages game-related commands such as save, restore, and stop.

- **Commands**:
  - `/stop`: Stops the server after saving the current game state.
  - `/restore`: Restores a previous game state based on a given index.
  - `/save`: Saves the current game state.
  - `/newGame`: Starts a new game with specified configurations.

## Contributing

If you'd like to contribute to this project:

1. Fork the repository.
2. Create a new feature branch.
3. Commit your changes and push them to your fork.
4. Create a pull request.

Please ensure your code follows the existing coding conventions and passes all tests.


## Contact

For any inquiries, please contact Antonio Scalia at [antoniosalvatores@gmail.com](mailto:antoniosalvatores@gmail.com).