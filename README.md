# Matrix Hacker: A Command-Line Cyber-Simulation

## Project Overview

Matrix Hacker is a Python-based, text-driven cyber-simulation game designed to immerse players in a command-line interface (CLI) environment, challenging them with network navigation, data retrieval, and strategic problem-solving. Developed with a strong emphasis on modularity, scalability, and maintainability, this project serves as a robust demonstration of software engineering principles applied to interactive game development.

## Key Features & Technical Highlights

*   **Dynamic Quest Generation System:**
    *   Implemented a sophisticated, template-driven quest engine capable of generating diverse missions across multiple difficulty tiers (Easy, Medium, Hard).
    *   Quests are dynamically tailored to player progression, available commands, and current "street cred," ensuring a personalized and challenging experience.
    *   Features intelligent quest selection algorithms that prioritize new command introduction, avoid repetition, and guide players through a progressive learning curve.
    *   Dynamically provisions in-game network assets (servers, files, directories) on remote IPs based on quest requirements, enhancing realism and replayability.
*   **Modular Network Simulation:**
    *   Designed an extensible in-game network layer with abstract `Server`, `File`, and `Directory` classes.
    *   Simulates core networking protocols (`ping`, `ssh`, `nmap`, ``portscan`, `grep`, `find`, `tcpdump`) allowing for realistic command-line interaction and extensible future development.
*   **Command-Line Interface (CLI) Engine:**
    *   Developed a responsive and intuitive text-based interface, providing a core interaction loop for command input and output.
    *   Features a comprehensive help system, dynamic command availability, and robust input parsing.
*   **Game State Management & Persistence:**
    *   Implemented a clear separation of game state logic, ensuring maintainability and enabling future features like persistent save/load functionality.
*   **Scalability & Maintainability Focus:**
    *   Architected the project with clear separation of concerns (e.g., UI, core game logic, quest generation, network simulation) to facilitate independent development and future expansion.
    *   Utilized data-driven design patterns (e.g., `QUEST_TEMPLATES`) to allow for easy addition of new content without code modification.

## My Contributions

As the primary developer for this project overhaul, my responsibilities and contributions included:

*   **Architectural Redesign:** Led the complete re-architecture of the game's core systems, transitioning from a monolithic structure to a modular, layered design.
*   **Quest System Development:** Designed and implemented the entire dynamic quest generation pipeline, including:
    *   Defining new, comprehensive quest templates with tiered difficulty and explicit command requirements.
    *   Developing the intelligent quest selection algorithm to ensure progressive challenge and command utilization.
    *   Implementing the dynamic creation and placement of quest-specific network targets (remote servers, files, hidden data).
    *   Refining quest objective clarity and in-game guidance.
*   **Core Game Logic Refinement:** Enhanced existing game mechanics, suchs as the intel panel, command handling, and player progression, to integrate seamlessly with the new quest system.
*   **Debugging & Quality Assurance:** Systematically identified and resolved complex bugs, including critical `IndentationError` and `NameError` issues, demonstrating strong debugging and problem-solving skills.
*   **Code Quality & Documentation:** Ensured adherence to Python best practices, improved code readability, and updated project documentation (`requirements.txt`, `README.md`) to reflect the project's advanced state.

## Technical Stack

*   **Language:** Python 3.x
*   **Game Library:** Pygame (for rendering and event handling)
*   **Core Concepts:** Object-Oriented Programming (OOP), Event-Driven Architecture, Data-Driven Design, CLI Development, Network Simulation.

## Installation & Setup

To run this project locally:

1.  **Clone the repository:**
    ```bash
    git clone [Your Repository URL Here]
    cd Matrix_Hacker
    ```
    *(Replace `[Your Repository URL Here]` with the actual URL of the repository.)*

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

## Future Enhancements

*   Implementation of a persistent save/load system for game progress.
*   Expansion of network types and vulnerabilities.
*   Development of a more complex narrative branching system.