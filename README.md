#  Virtual Hand Controller

This Python application transforms your webcam into a **virtual controller**, allowing you to control your computer's mouse and type on an on-screen keyboard using only hand gestures.  
It leverages **real-time hand tracking** to create an intuitive and futuristic human-computer interface.

---

##  Features

- **Virtual Mouse:** Control the cursor's movement by moving your index finger.  
- **Gesture-Based Clicking:** Perform a left-click by pinching your thumb and index finger together.  
- **On-Screen Keyboard:** A fully functional keyboard is displayed on the screen.  
- **Hover-to-Type:** Simply hover your index finger over a key for a moment to type, creating a smooth and seamless experience.  
- **Real-Time Feedback:** Displays your webcam feed with hand landmarks, highlights the hovered key, and shows your typed text.

---

##  Tech Stack

- **Python 3.10**
- **OpenCV** → Webcam access and image processing  
- **MediaPipe** → Robust real-time hand tracking  
- **PyAutoGUI** → Programmatic mouse and keyboard control  
- **NumPy** → Numerical operations and data interpolation  

---

##  Getting Started

Follow these steps to run the project locally.

### 1. Prerequisites
Make sure **Python 3.10 (64-bit)** is installed.  
 [Download Python](https://www.python.org/downloads/release/python-31011/)

### 2. Setup and Installation

```bash
# Clone the repository
git clone https://github.com/jeet2005/Virtual-Hand-Controller
cd Virtual-Hand-Controller

# Create and activate a virtual environment
python -m venv venv

# Activate on Windows
.\venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### 3. Setup and Installation

```bash
python virtual_controller.py
```

A window showing your webcam feed will appear. You can now control your system with your hand!

---

##  How to Use

| **Action** | **Gesture** |
|-------------|-------------|
| **Move Cursor** | Move your index finger around |
| **Left Click** | Pinch your index finger and thumb together |
| **Type a Key** | Hover your index finger over a key for ~0.5 seconds |
| **Quit** | Press **Q** on your physical keyboard |

---

##  Troubleshooting

- Ensure your webcam is not in use by another app.  
- Run the script in a **well-lit environment** for better hand tracking.  
- On Windows, run the terminal as **Administrator** if PyAutoGUI fails to control the mouse.

---

##  requirements.txt

Include this file in your project directory so others can easily install dependencies.

```text
opencv-python
mediapipe
pyautogui
numpy
```

---

##  License

Licensed under the MIT License © 2025 Jeet Savaliya

