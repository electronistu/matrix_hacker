# Matrix Hacker

A text-based hacking simulation game where players navigate a digital world, execute commands, and complete quests to uncover a deeper narrative.

## Description

Dive into the role of an operative in a cyberpunk-inspired world. Interact with servers, explore file systems, and engage in network operations through a command-line interface. Unravel a mysterious story by completing dynamically generated quests, earning currency, and upgrading your hacking toolkit. Be mindful of your system trace, as too much activity can lead to detection!

## Features

*   **Immersive CLI Experience:** Interact with the game world using familiar terminal commands (`ls`, `cat`, `cd`, `ssh`, `ping`, `grep`, `find`, `nmap`, `tcpdump`, `portscan`).
*   **Dynamic Quest System:** Undertake missions that adapt to your progress, street cred, and available commands. Discover objectives by exploring server files and intel.
*   **In-Game Economy:** Earn "Creds" and "Chips" to purchase new software (commands) and hardware upgrades from the black market.
*   **Network Exploration:** Traverse a simulated network of interconnected servers, each with its own file system, users, and secrets.
*   **Intel Panel:** A dedicated HUD displays crucial information, including known IPs, credentials, and mission-critical data.
*   **System Trace Mechanic:** Every action carries a risk. Manage your system trace to avoid detection and game over.
*   **Rich Lore:** Uncover fragments of a compelling narrative hidden within the network.

## How to Play

1.  **Start the Game:** Run `main.py`.
2.  **Main Menu:** Choose to start a new game or load a previous save.
3.  **Terminal Interaction:**
    *   Type commands into the console at the bottom of the screen.
    *   Use `help` to see a list of available commands or `help <command>` for specific command details.
    *   Use `list quests` to view available and active missions.
    *   Use `accept <quest_id>` to begin a quest.
    *   Follow quest descriptions to find objectives. For "deliver" quests, you'll often need to find a specific keyword or item within a file and then use `deliver <keyword_or_item>`.
    *   Navigate directories with `ls` and `cd`.
    *   View file contents with `cat`.
    *   Connect to remote servers with `ssh <user>@<ip>`.
    *   Monitor your "SYSTEM TRACE" on the right panel. If it reaches 100%, it's game over.
4.  **Market:** Visit the black market server (`ssh market@13.37.13.37`) to `list` and `buy` new software and hardware.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/Matrix_Hacker.git
    cd Matrix_Hacker
    ```
    *(Note: Replace `https://github.com/your-repo/Matrix_Hacker.git` with the actual repository URL if available.)*

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    ```

3.  **Activate the virtual environment:**
    *   On Linux/macOS:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the game:**
    ```bash
    python main.py
    ```

## Credits

*   **Developer:** [Radu Tataru-Marinescu]
*   **Inspired by:** Classic hacking games and cyberpunk themes.
