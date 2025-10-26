# Train Robbery: An Old School Cyber Heist 🚂💰
By: Luke Alvarado, Edison La, Jamie Nwachukwu

Embark on a thrilling train heist adventure! This project combines interactive shell scripting with Python-based ASCII art and educational cybersecurity simulations. The core objective is to guide users through a narrative where they plan and execute a virtual train robbery, encountering various security challenges along the way. It's designed to be both entertaining and educational, providing hands-on experience with cybersecurity concepts.

## 🚀 Key Features

*   **Interactive Narrative:** A shell script guides users through the train robbery scenario with engaging story elements, teaching basics of common cyber exploits.
*   **ASCII Art Visuals:** Python scripts generate visually appealing ASCII art of trains, gold, keys, and other thematic elements.
*   **Cybersecurity Simulations:** Integrated training carts simulate real-world cybersecurity threats like DDoS attacks, buffer overflows, and SQL injection.
*   **Educational Focus:** Provides practical experience with identifying and mitigating common security vulnerabilities.
*   **Modular Design:** The project is structured into separate modules for narrative, visuals, and simulations, making it easy to extend and customize.

## 🛠️ Tech Stack

*   **Shell Scripting:** `bash` (for the main game orchestration)
*   **Python:**
    *   `PIL (Pillow)`: Image processing for ASCII art conversion.
    *   `pyfiglet`: Text to ASCII art conversion.
    *   `ipywidgets`: Interactive UI elements (potentially).
    *   `IPython.display`: Displaying HTML content in IPython environments.
    *   `pathlib`: File path manipulation.
    *   `io`: Input/output operations.
    *   `time`: Time-related functions for animations.
    *   `textwrap`: For formatting text.
    *   `subprocess`: For launching external processes.
    *   `shutil`: For file operations.
    *   `os`: Interacting with the operating system.
    *   `sys`: Interacting with the Python runtime environment.
*   **C:**
    *   Standard C libraries (`stdio.h`, `stdlib.h`, `string.h`, `unistd.h`, `arpa/inet.h`, `errno.h`, `sys/types.h`, `sys/wait.h`) for server implementations.
*   **Networking:** TCP/IP Sockets
*   **Environment:** IPython (Jupyter Notebook) for some visual components.

## 📦 Getting Started

### Prerequisites

*   **Bash:** Ensure you have a bash shell environment.
*   **Python 3:** Python 3.x must be installed.
*   **Python Packages:** Install the necessary Python packages using `pip`:

    ```bash
    pip install Pillow pyfiglet ipywidgets
    ```

*   **C Compiler:** A C compiler (like GCC) is required to compile the C server programs.

### Installation

1.  **Clone the Repository:**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install pyfiglet:**

    ```bash
    pip install pyfiglet
    ```

### Running Locally

1.  **Navigate to the `theBigOne` directory:**

    ```bash
    cd theBigOne
    ```

2.  **Run the main script:**

    ```bash
    bash theBigOne.sh
    ```

    This will start the train robbery narrative and launch the associated Python scripts and C programs.

3.  **For Jupyter Notebook Components:** Open the relevant Python files (e.g., `Python-folder/Gold.py`, `theBigOne/NuclearEngine/eng.py`) in a Jupyter Notebook environment to view the ASCII art and animations.

4.  **Running C server programs:**
    * Navigate to the directory containing the C file (e.g., `theBigOne/galacticMail/`).
    * Compile the C program: `gcc cart-3.c -o cart-3`
    * Run the compiled program: `./cart-3`
    * Compile all the c programs in the respective cart folders, including the vault
    * Make sure to run all the scripts in the cart folders that start the nc connections
    * Each has to be a running process, so that the user can connect and use

## 📂 Project Structure

```
├── Python-folder
│   ├── Gyro.py
│   ├── TrainASCII.py
│   ├── Gold.py
│   ├── Question-Mark.py
│   ├── Key.py
│   └── Start.py
├── theBigOne
│   ├── theBigOne.sh
│   ├── train.py
│   ├── train_menu.py
│   ├── question.py
│   ├── NuclearEngine
│   │   └── eng.py
│   ├── galacticMail
│   │   ├── cart-3.c
│   │   └── sqlTraining.c
│   └── quantumHolding
│       ├── quant.py
│       └── cart-2.c
└── README.md
```

## 💖 Thanks
Contributions are welcome for creating new carts! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with descriptive messages.
4.  Submit a pull request

Thank you for checking out the Train Robbery project! I hope you find it both entertaining and educational. Your feedback and contributions are greatly appreciated!


