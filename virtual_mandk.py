import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time

# --- Constants and Initialization ---
# Disable the PyAutoGUI fail-safe for edge-to-edge control
pyautogui.FAILSAFE = False

# --- Button Class for Keyboard ---
class Button:
    """A class to create and manage an on-screen button."""
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text

    def draw(self, img, alpha=0.5):
        """Draw the button on the image with transparency."""
        x, y = self.pos
        w, h = self.size
        
        # Create a semi-transparent rectangle
        overlay = img.copy()
        cv2.rectangle(overlay, self.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

        # Add text to the button
        font_scale = 3 if len(self.text) > 1 else 4
        text_offset_x = 10 if len(self.text) > 1 else 20
        cv2.putText(img, self.text, (x + text_offset_x, y + 65), 
                    cv2.FONT_HERSHEY_PLAIN, font_scale, (255, 255, 255), 4)

def main():
    """
    Main function to run the virtual mouse and keyboard application.
    """
    # --- Webcam and Hand Tracking Setup ---
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    cap.set(3, 1280)  # Set width
    cap.set(4, 720)   # Set height

    # MediaPipe Hands initialization
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    mp_draw = mp.solutions.drawing_utils

    # --- Keyboard Setup ---
    keys = [
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "<-"]
    ]
    button_list = []
    for i in range(len(keys)):
        for j, key in enumerate(keys[i]):
            button_list.append(Button([100 * j + 50, 100 * i + 50], key))
    # Add a space bar separately for custom size
    button_list.append(Button([250, 350], "Space", size=[400, 85]))

    # --- System and Control Variables ---
    screen_width, screen_height = pyautogui.size()
    frame_reduction = 100
    
    # Smoothing variables
    smoothening = 7
    prev_x, prev_y = 0, 0
    curr_x, curr_y = 0, 0
    
    # Text display and hover-to-type variables
    typed_text = ""
    hover_start_time = 0
    hovered_button = None
    HOVER_DURATION = 0.5 # seconds to hover to type

    # --- Main Application Loop ---
    while True:
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # --- Draw UI Elements ---
        # Draw keyboard
        for button in button_list:
            button.draw(frame)
        # Draw the text display box
        cv2.rectangle(frame, (50, 450), (1050, 550), (175, 0, 175), cv2.FILLED)
        cv2.putText(frame, typed_text, (60, 515), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

        finger_on_key = False # Flag to reset hover timer

        # --- Hand Landmark Processing ---
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

            frame_height, frame_width, _ = frame.shape
            ix, iy = int(index_tip.x * frame_width), int(index_tip.y * frame_height)
            tx, ty = int(thumb_tip.x * frame_width), int(thumb_tip.y * frame_height)

            # --- 1. Cursor Movement ---
            screen_x = np.interp(ix, (frame_reduction, frame_width - frame_reduction), (0, screen_width))
            screen_y = np.interp(iy, (frame_reduction, frame_height - frame_reduction), (0, screen_height))
            curr_x = prev_x + (screen_x - prev_x) / smoothening
            curr_y = prev_y + (screen_y - prev_y) / smoothening
            pyautogui.moveTo(curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

            # --- 2. Left Click Gesture (Thumb + Index) ---
            click_distance = math.hypot(tx - ix, ty - iy)
            if click_distance < 40:
                cv2.circle(frame, (ix, iy), 15, (0, 255, 0), cv2.FILLED)
                pyautogui.click()
                time.sleep(0.2)

            # --- 3. Hover-to-Type Gesture ---
            for button in button_list:
                x, y = button.pos
                w, h = button.size

                if x < ix < x + w and y < iy < y + h:
                    finger_on_key = True
                    button.draw(frame, alpha=0.2) # Highlight hovering key

                    if hovered_button != button:
                        hovered_button = button
                        hover_start_time = time.time()
                    
                    hover_time = time.time() - hover_start_time
                    if hover_time > HOVER_DURATION:
                        # Handle key press action
                        if button.text == "<-":
                            typed_text = typed_text[:-1]
                        elif button.text == "Space":
                            typed_text += " "
                        else:
                            typed_text += button.text
                        pyautogui.press(button.text if len(button.text) == 1 else 'backspace' if button.text == '<-' else 'space')

                        # Reset after typing to prevent multiple presses
                        hovered_button = None 
                        hover_start_time = 0

        # If finger is not on any key, reset hover state
        if not finger_on_key:
            hovered_button = None
            hover_start_time = 0

        cv2.imshow("Virtual Controller", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # --- Cleanup ---
    cap.release()
    cv2.destroyAllWindows()
    hands.close()

if __name__ == "__main__":
    main()

