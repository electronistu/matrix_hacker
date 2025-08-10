# Matrix Hacker: The Genesis Echo

**A narrative-driven, procedurally generated hacking simulation in a retro-futuristic terminal.**

![Gameplay Screenshot](screenshot.png)
*(Note: Add a gameplay screenshot or GIF here)*

---

## Core Concept

Step into the role of a "Data Archaeologist" in a world of digital ghosts and corporate espionage. You are hired by the enigmatic **Chronosync** corporation to explore the ruins of the Aethelred Sub-Net, a decommissioned sector of the old internet. Your mission is to recover lost data fragments from a top-secret project, all while evading a rival entity, the **Singularity Foundation**, who are chasing their own ghosts in the machine.

But as you delve deeper, the fragments you collect begin to tell a different story—a story that was never meant to be found.

## Key Features

*   **Procedurally Generated Campaign:** Every playthrough is a unique experience. The game generates a new campaign with a unique chain of networks, servers, and clues each time you play.
*   **Learn as You Play:** Start with basic commands and learn more powerful, realistic tools like `grep` and `tcpdump` by finding `.hlp` files in the game world. The campaign is designed to teach you how to use these tools organically.
*   **Layered Narrative:** Uncover the truth by peeling back the layers of the story. What begins as a simple data recovery mission evolves into a deep, psychological mystery about the nature of consciousness and reality itself.
*   **Immersive Terminal Interface:** A retro-futuristic CRT aesthetic with scanlines, a dynamic grid, and a focus on a pure, keyboard-driven experience.
*   **Clean & Modular Architecture:** Built with a professional, multi-file structure that separates concerns (game logic, UI, core systems, campaign generation) for scalability and maintainability.

## How to Play

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/matrix-hacker.git
    cd matrix-hacker
    ```

2.  **Set up a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the game:**
    ```bash
    python3 main.py
    ```

## Project Structure

This project is built with a clean, modular architecture, making it easy to understand, maintain, and extend.

```
matrix-hacker/
├── core/               # Core game logic (filesystem, network, commands)
├── ui/                 # UI components (console, map, trace bar)
├── campaign/           # Procedural generation and lore
├── main.py             # Main application entry point
├── game.py             # Core Game class and state management
├── settings.py         # Game constants and configuration
└── requirements.txt    # Project dependencies
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
*Copyright (c) 2025 Radu Tataru-Marinescu*
