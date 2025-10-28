# Virtual Hand Controller

<div align="center">

![Project Banner](https://raw.githubusercontent.com/jeet2005/Virtual-Hand-Controller/main/assets/banner.png) <!-- TODO: Create and add an appealing project banner -->

[![GitHub stars](https://img.shields.io/github/stars/jeet2005/Virtual-Hand-Controller?style=for-the-badge)](https://github.com/jeet2005/Virtual-Hand-Controller/stargazers)

[![GitHub forks](https://img.shields.io/github/forks/jeet2005/Virtual-Hand-Controller?style=for-the-badge)](https://github.com/jeet2005/Virtual-Hand-Controller/network)

[![GitHub issues](https://img.shields.io/github/issues/jeet2005/Virtual-Hand-Controller?style=for-the-badge)](https://github.com/jeet2005/Virtual-Hand-Controller/issues)

[![License](https://img.shields.io/github/license/jeet2005/Virtual-Hand-Controller?style=for-the-badge)](LICENSE)

**A Python app that transforms your webcam into an intuitive, gesture-based virtual mouse and keyboard.**

</div>

## Overview

The Virtual Hand Controller is an innovative desktop utility that leverages computer vision to provide a hands-free interface for your computer. By utilizing your webcam, MediaPipe for advanced hand tracking, and OpenCV for real-time video processing, this application enables you to control your mouse movements, clicks, and even keyboard inputs through natural hand gestures.

Designed for accessibility, interactive presentations, or simply a novel way to interact with your digital world, the Virtual Hand Controller offers a seamless and engaging experience, making your physical hand an extension of your digital input.

## Features

-   **Real-time Hand Tracking:** Utilizes MediaPipe for robust and accurate detection of hand landmarks.
-   **Dynamic Virtual Mouse Control:**
    -   Seamless mouse cursor movement based on hand position.
    -   Single-finger "click" gesture for left-click functionality.
    -   Two-finger "click" gesture for right-click functionality.
    -   Vertical scrolling simulation using specific hand gestures.
-   **Intuitive Virtual Keyboard Input:**
    -   Configurable gestures to trigger keyboard key presses (e.g., 'W', 'A', 'S', 'D').
    -   Potentially supports basic typing or command execution via hand poses.
-   **Visual Feedback:** Displays the live webcam feed with superimposed hand landmarks and recognized gestures, providing clear visual confirmation of interaction.
-   **Cross-platform Compatibility:** Built with Python, making it compatible with various operating systems.
-   **Zero-touch Interaction:** Offers a completely touch-free way to control your system.


![Screenshot of hand tracking controlling mouse](https://raw.githubusercontent.com/jeet2005/Virtual-Hand-Controller/main/assets/screenshot-1.png)
_Example: Hand controlling mouse cursor on screen_

![Screenshot of gesture for keyboard input](https://raw.githubusercontent.com/jeet2005/Virtual-Hand-Controller/main/assets/screenshot-2.png)
_Example: Recognized gesture triggering a keyboard event_

## Tech Stack

-   **Runtime:**
    [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
-   **Computer Vision & Input Control:**
    [![MediaPipe](https://img.shields.io/badge/MediaPipe-FF0000?style=for-the-badge&logo=googlegemini&logoColor=white)](https://developers.google.com/mediapipe)
    [![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
    [![PyAutoGUI](https://img.shields.io/badge/PyAutoGUI-000000?style=for-the-badge)](https://pyautogui.readthedocs.io/en/latest/)

## Quick Start

Follow these steps to get the Virtual Hand Controller up and running on your local machine.

### Prerequisites

Before you begin, ensure you have the following installed:

-   **Python 3.x**: Download from [python.org](https://www.python.org/downloads/)
-   **A functional webcam**: Required for hand tracking.

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/jeet2005/Virtual-Hand-Controller.git
    cd Virtual-Hand-Controller
    ```

2.  **Install dependencies**
    Use `pip` to install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Controller

1.  **Execute the main script**
    Navigate to the project directory and run the `virtual_mandk.py` file:
    ```bash
    python virtual_mandk.py
    ```

    Upon execution, a window displaying your webcam feed will appear. This window will also show the detected hand landmarks and provide visual cues for recognized gestures.

## Usage

Once the application is running, position your hand in front of your webcam. The application will detect your hand and provide visual feedback on the screen.

While specific gesture mappings are defined within the `virtual_mandk.py` script, here are some common inferred interactions:

-   **Mouse Movement:** Move your hand to move the mouse cursor. The tip of your index finger often acts as the pointer.
-   **Left Click:** A specific gesture, such as bringing your thumb and index finger together (a pinch gesture) or a quick closed fist, will likely trigger a left mouse click.
-   **Right Click:** A different gesture, potentially involving two fingers or a variation of the click gesture, may trigger a right mouse click.
-   **Scrolling:** Vertical movement of your hand or a specific two-finger gesture could enable scrolling.
-   **Keyboard Input:** Certain static hand poses or dynamic gestures might be mapped to specific keyboard keys (e.g., a "W" shape for 'W' key).

Refer to the source code in `virtual_mandk.py` for the exact gesture definitions and their corresponding actions.

## Project Structure

```
Virtual-Hand-Controller/
├── .gitignore          # Specifies intentionally untracked files to ignore
├── LICENSE             # MIT License file
├── README.md           # This documentation file
├── requirements.txt    # List of Python dependencies
└── virtual_mandk.py    # The main Python application script
```

## ⚙️ Configuration & Customization

The core logic and gesture mappings are defined within the `virtual_mandk.py` script. For advanced users and developers, customization can be done by modifying this file directly:

-   **Gesture Definitions:** Adjust the `if/elif` conditions that check for specific hand landmark positions and distances to modify or add new gestures.
-   **Sensitivity:** Parameters related to detection thresholds or movement sensitivity can be fine-tuned.
-   **Keyboard Mappings:** Change which keyboard keys are triggered by which gestures.

## Contributing

We welcome contributions to enhance the Virtual Hand Controller! If you have ideas for new features, improvements, or bug fixes, please feel free to:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature`).
3.  Make your changes and ensure the code adheres to best practices.
4.  Commit your changes (`git commit -m 'feat: Add new gesture for X'`).
5.  Push to the branch (`git push origin feature/your-feature`).
6.  Open a Pull Request.

### Development Setup for Contributors

Simply follow the **Quick Start** installation steps. All development can be done by modifying the `virtual_mandk.py` file directly.

## License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

-   [Google MediaPipe](https://developers.google.com/mediapipe) for the robust hand tracking solution.
-   [OpenCV](https://opencv.org/) for powerful computer vision capabilities.
-   [PyAutoGUI](https://pyautogui.readthedocs.io/en/latest/) for cross-platform GUI automation.

## Support & Contact

-   **Issues:** Report bugs or suggest features on the [GitHub Issues page](https://github.com/jeet2005/Virtual-Hand-Controller/issues).
-   **Author:** [jeet2005](https://github.com/jeet2005)
