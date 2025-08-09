# Matrix Hacker

A narrative-driven, roguelike hacking simulation and interactive Bash tutorial built with Python and Pygame.

---

## Synopsis

`Matrix Hacker` is a single-player, immersive terminal-based game where the player takes on the role of an operative guided by a mysterious entity known as "Control." Each run, the player is tasked with infiltrating a unique, procedurally generated ghost network to uncover the secrets of a defunct project, codenamed "Genesis."

The game is a pure roguelike experience designed to be a compelling, story-driven tutorial for command-line fundamentals. The player starts with only the most basic commands and must learn new ones like `ssh`, `cd`, and `nmap` by finding and reading help files scattered across the network. The narrative unfolds through a trail of logs and encrypted files, leading the player through the network to the ultimate prize: the truth behind the Genesis Project.

## Core Features

*   **Realistic Terminal Simulation:** All interaction is handled through a simulated Bash shell, providing an immersive hacking experience.
*   **Procedural Network Generation:** Every playthrough features a new, randomly generated network of servers, ensuring infinite replayability and a fresh challenge every time.
*   **Learn-by-Doing Mechanics:** The player's command set expands as they explore. New commands are unlocked by finding and reading `.hlp` files, seamlessly integrating the learning process into the gameplay.
*   **Layered Mystery:** The player uncovers two layers of lore: the surface story of the "Aethelred" project and the deeper, hidden mystery of the "RKSE" (Radu-Kelly Symbiotic Engine) hidden in the system's logs and notes.
*   **Organic Discovery:** There is no hand-holding. The player must follow a breadcrumb trail of clues found in files to discover new server IPs, credentials, and the path to the root server.

## Technology Stack

*   **Language:** Python 3
*   **Core Library:** Pygame (for the game loop, rendering, and event handling)
*   **Procedural Generation:** NumPy and SciPy (for network graph generation)

## Setup and Installation

To run the project locally, please follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd Matrix_Hacker
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies from `requirements.txt`:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the game:**
    ```bash
    python main.py
    ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*Developed by Radu Tataru-Marinescu*