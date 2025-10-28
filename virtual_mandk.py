import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time

# --- Constants and Initialization ---
pyautogui.FAILSAFE = False

# System Control Constants
ZOOM_THRESHOLD = 30 # Reduced for persistence stability
SLIDE_THRESHOLD = 40 
CLICK_DISTANCE = 40 
COOLDOWN_TIME = 0.5 
PERSISTENCE_FRAMES = 5 # How many frames a gesture must be held to trigger
BTN_W, BTN_H = 100, 40 

# Drawing Constants
DRAW_COLOR = (0, 255, 255) 
DRAW_THICKNESS = 15

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
        
        # Determine color based on text
        if self.text == "YES":
            btn_color = (0, 200, 0)
        elif self.text == "NO":
            btn_color = (0, 0, 200)
        elif self.text in ["KBD", "DRAW"]:
            btn_color = (255, 165, 0)
        else:
            btn_color = (255, 0, 255)

        # Draw transparent rectangle
        overlay = img.copy()
        rect_alpha = 0.9 if self.text in ["YES", "NO", "KBD", "DRAW"] else alpha
        
        cv2.rectangle(overlay, self.pos, (x + w, y + h), btn_color, cv2.FILLED)
        cv2.addWeighted(overlay, rect_alpha, img, 1 - rect_alpha, 0, img)

        # Add text
        if self.text in ["YES", "NO", "KBD", "DRAW"]:
            font_scale = 1.5
            text_offset_x = 10
            text_offset_y = 30
            text_thickness = 3
        else:
            font_scale = 3 if len(self.text) > 1 else 4
            text_offset_x = 10
            text_offset_y = 65
            text_thickness = 4
        
        cv2.putText(img, self.text, (x + text_offset_x, y + text_offset_y), 
                    cv2.FONT_HERSHEY_PLAIN, font_scale, (255, 255, 255), text_thickness)


def show_intro(cap, frame_width, frame_height):
    """Displays the 'Welcome STARK' pulsating intro screen."""
    start_time = time.time()
    duration = 2.0
    
    while time.time() - start_time < duration:
        success, frame = cap.read()
        if not success:
            continue
        
        frame = cv2.flip(frame, 1)
        intro_frame = np.zeros((frame_height, frame_width, 3), np.uint8)
        
        elapsed = time.time() - start_time
        
        pulse = 1.0 + 0.5 * math.sin(elapsed * math.pi * 3) 
        
        text = "Welcome STARK"
        font_scale = 2.0 + 0.5 * pulse
        thickness = int(3 + 2 * pulse)
        
        text_size, baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, font_scale, thickness)
        text_x = (frame_width - text_size[0]) // 2
        text_y = (frame_height + text_size[1]) // 2

        color = (255, 255, 0) # Bright Cyan/Blue
        
        cv2.putText(intro_frame, text, (text_x, text_y), 
                    cv2.FONT_HERSHEY_DUPLEX, font_scale, color, thickness)
        
        cv2.imshow("Virtual Controller", intro_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def main():
    """
    Main function to run the virtual mouse, keyboard, and system control application.
    """
    # --- Webcam and Hand Tracking Setup ---
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    # --- NEW: Get screen resolution for full-screen app ---
    screen_width, screen_height = pyautogui.size()
    frame_width = screen_width
    frame_height = screen_height
    
    # Set camera capture resolution (can be lower than screen res)
    cap.set(3, 1280)  
    cap.set(4, 720)   

    # --- Introduction Screen ---
    show_intro(cap, frame_width, frame_height)
    
    # --- NEW: Set OpenCV window to full-screen ---
    cv2.namedWindow("Virtual Controller", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Virtual Controller", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


    # MediaPipe Hands initialization - Set max_num_hands to 2
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=2,
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
    # --- NEW: Center the keyboard ---
    keyboard_width = 1035 # Approx width of 10 keys + padding
    keyboard_x_offset = (frame_width - keyboard_width) // 2

    for i in range(len(keys)):
        for j, key in enumerate(keys[i]):
            button_list.append(Button([keyboard_x_offset + 100 * j + 50, 100 * i + 100], key))
    button_list.append(Button([keyboard_x_offset + 250, 420], "Space", size=[400, 85]))

    # --- Mode Switch Buttons ---
    # Positioned at the top right of the frame
    btn_kbd = Button([frame_width - 2*BTN_W - 30, 20], "KBD", size=[BTN_W, BTN_H])
    btn_draw = Button([frame_width - BTN_W - 20, 20], "DRAW", size=[BTN_W, BTN_H])
    switch_buttons = [btn_kbd, btn_draw]

    # --- System and Control Variables ---
    screen_width, screen_height = pyautogui.size()
    frame_reduction = 100 
    
    # Smoothing variables (Touchpad Mode)
    smoothening = 7
    prev_x, prev_y = 0, 0
    curr_x, curr_y = 0, 0
    
    # Typing variables
    typed_text = ""
    hover_start_time = 0
    hovered_button = None
    HOVER_DURATION = 0.5 

    # State variables
    keyboard_active = False
    is_drawing_mode_active = False 
    confirm_state = None 
    
    # Confirmation Hover Variables 
    confirm_hover_button = None 
    confirm_hover_start_time = 0
    
    # Drawing variables
    drawing_canvas = None
    prev_draw_point = None
    
    # Gesture tracking
    last_action_time = 0
    
    # Cooldown variables for single-hand gestures
    last_zoom_distance = 0
    gesture_start_x = None
    
    # NEW PERSISTENCE TRACKING
    zoom_persistence_count = 0
    swipe_persistence_count = 0
    
    # --- NEW: Re-add Camera Feed Display Constants ---
    CAM_W = 300
    CAM_H = 200
    CAM_X = frame_width - CAM_W - 20
    CAM_Y = 80 # Below the top status bar

    # --- Main Application Loop ---
    while True:
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Flip the original frame for natural interaction
        original_frame = cv2.flip(frame, 1)
        
        # 1. Create the dark "Desktop Hub" background
        desktop_canvas = np.zeros((frame_height, frame_width, 3), np.uint8) 
        
        # 2. Process landmarks on the original flipped frame
        rgb_frame = cv2.cvtColor(original_frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # Initialize drawing canvas
        if drawing_canvas is None:
            drawing_canvas = np.zeros((frame_height, frame_width, 3), np.uint8)

        hand_count = len(results.multi_hand_landmarks) if results.multi_hand_landmarks else 0
        
        # --- UI BASE LAYER: Status Bars and Panels ---
        
        # Status Bar (Top)
        cv2.rectangle(desktop_canvas, (0, 0), (frame_width, 70), (20, 20, 20), cv2.FILLED) 
        # Bottom Bar for notepad/feedback
        cv2.rectangle(desktop_canvas, (0, frame_height - 140), (frame_width, frame_height), (20, 20, 20), cv2.FILLED) 
        
        # --- Draw Status UI ---
        status_text = "STATUS: Touchpad Active"
        status_color = (0, 255, 0) # Green
        
        if keyboard_active:
            status_text = "STATUS: KEYBOARD MODE"
            status_color = (255, 0, 255) # Magenta
        elif is_drawing_mode_active:
             status_text = "STATUS: DRAWING MODE"
             status_color = (255, 255, 0) # Cyan
        
        cv2.putText(desktop_canvas, status_text, (20, 45), cv2.FONT_HERSHEY_DUPLEX, 1, status_color, 2)
        
        # Draw Mouse Detection Area Boundary (on the desktop canvas)
        cv2.rectangle(desktop_canvas, (frame_reduction, frame_reduction), 
                      (frame_width - frame_reduction, frame_height - frame_reduction), 
                      (status_color[0], status_color[1], status_color[2]), 2) 

        # --- Draw Notepad Display Area (Bottom Panel) ---
        # NEW: Centered Notepad
        NOTEPAD_WIDTH = 1000
        NOTEPAD_X = (frame_width - NOTEPAD_WIDTH) // 2
        NOTEPAD_Y = frame_height - 120
        NOTEPAD_HEIGHT = 60

        cv2.putText(desktop_canvas, "NOTEPAD:", (NOTEPAD_X + 5, NOTEPAD_Y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 200, 255), 1) 
        cv2.putText(desktop_canvas, typed_text, (NOTEPAD_X + 5, NOTEPAD_Y + 45), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2) 
        
        # --- NEW: Re-add Embed Camera Feed (Top Right) ---
        cam_feed_resized = cv2.resize(original_frame, (CAM_W, CAM_H))
        desktop_canvas[CAM_Y:CAM_Y+CAM_H, CAM_X:CAM_X+CAM_W] = cam_feed_resized
        
        # Draw border around embedded camera feed
        cv2.rectangle(desktop_canvas, (CAM_X, CAM_Y), (CAM_X + CAM_W, CAM_Y + CAM_H), (255, 255, 255), 2)


        # --- Hand Landmark Processing & Control ---
        if hand_count > 0:
            
            # --- NEW: Draw all detected hand skeletons on the main canvas ---
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(desktop_canvas, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # --- Control logic still uses the FIRST hand (h1) ---
            h1 = results.multi_hand_landmarks[0]
            
            # Get all landmark lists for h1 (mapped to ORIGINAL frame coordinates)
            lm_list = [(int(lm.x * frame_width), int(lm.y * frame_height)) for lm in h1.landmark]
            
            # Extract key tips (mapped to ORIGINAL frame coordinates)
            index_tip = h1.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = h1.landmark[mp_hands.HandLandmark.THUMB_TIP]
            
            ix = int(index_tip.x * frame_width)
            iy = int(index_tip.y * frame_height)
            tx = int(thumb_tip.x * frame_width)
            ty = int(thumb_tip.y * frame_height)
            
            # Cursor position (mapped to UI screen space for interaction with buttons)
            # When drawing on the desktop_canvas, we use (ix, iy). 
            
            # Check for general finger extensions/curls
            if len(lm_list) > 20:
                is_thumb_extended = lm_list[4][1] < lm_list[3][1]
                is_index_extended = lm_list[8][1] < lm_list[6][1]
                is_middle_extended = lm_list[12][1] < lm_list[10][1]
                is_ring_curled = lm_list[16][1] > lm_list[14][1]
                is_pinky_curled = lm_list[20][1] > lm_list[18][1]
                
                # Global Exit Trigger: Thumbs Up 
                is_thumbs_up_trigger = is_thumb_extended and not is_index_extended and \
                                       (lm_list[12][1] > lm_list[10][1]) and is_ring_curled and is_pinky_curled
                
                # --- CONFIRMATION LOGIC CHECK (Handles YES/NO buttons) ---
                if confirm_state is not None:
                    
                    CONFIRM_BOX_X_CENTER = frame_width // 2
                    CONFIRM_BOX_Y_CENTER = frame_height // 2
                    
                    YES_POS = [CONFIRM_BOX_X_CENTER - 150, CONFIRM_BOX_Y_CENTER + 10]
                    NO_POS = [CONFIRM_BOX_X_CENTER + 50, CONFIRM_BOX_Y_CENTER + 10]

                    btn_yes = Button(YES_POS, "YES", size=[BTN_W, BTN_H])
                    btn_no = Button(NO_POS, "NO", size=[BTN_W, BTN_H])
                    
                    # Display Question Overlay
                    confirm_overlay = desktop_canvas.copy()
                    cv2.rectangle(confirm_overlay, (frame_width//2 - 300, frame_height//2 - 70), 
                                  (frame_width//2 + 300, frame_height//2 + 70), (50, 50, 150), cv2.FILLED) 
                    desktop_canvas = cv2.addWeighted(desktop_canvas, 0.7, confirm_overlay, 0.3, 0) 

                    action = confirm_state.replace('_', ' ')
                    msg = f"Do you want to {action}?"
                    
                    cv2.putText(desktop_canvas, msg, (frame_width//2 - 290, frame_height//2 - 30), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 2)
                    
                    btn_yes.draw(desktop_canvas, alpha=0.9)
                    btn_no.draw(desktop_canvas, alpha=0.9)
                    
                    current_button_hover = None
                    
                    # 1. Check YES button hover
                    if YES_POS[0] < ix < YES_POS[0] + BTN_W and YES_POS[1] < iy < YES_POS[1] + BTN_H:
                        current_button_hover = 'YES'
                        btn_yes.draw(desktop_canvas, alpha=0.2) 

                    # 2. Check NO button hover
                    elif NO_POS[0] < ix < NO_POS[0] + BTN_W and NO_POS[1] < iy < NO_POS[1] + BTN_H:
                        current_button_hover = 'NO'
                        btn_no.draw(desktop_canvas, alpha=0.2) 
                    
                    
                    # 3. Handle hover time and action trigger
                    if current_button_hover is not None:
                        if confirm_hover_button != current_button_hover:
                            confirm_hover_button = current_button_hover
                            confirm_hover_start_time = time.time()

                        if time.time() - confirm_hover_start_time > HOVER_DURATION:
                            
                            action_result = confirm_hover_button 
                            
                            if action_result == 'YES':
                                
                                if confirm_state == 'EXIT_KEYBOARD':
                                    if typed_text:
                                        txt_file_path = f"notes_{int(time.time())}.txt"
                                        try:
                                            with open(txt_file_path, 'w') as f:
                                                f.write(typed_text)
                                            print(f"Typed text saved to {txt_file_path}")
                                        except Exception as e:
                                            print(f"Error saving text: {e}")
                                    keyboard_active = False
                                    typed_text = ""
                                    cv2.putText(desktop_canvas, "KEYBOARD EXITED & TEXT SAVED", (NOTEPAD_X, frame_height - 60), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
                                    
                                elif confirm_state == 'EXIT_DRAW':
                                    file_path = f"drawing_{int(time.time())}.jpg"
                                    try:
                                        cv2.imwrite(file_path, drawing_canvas)
                                        print(f"Drawing saved to {file_path}")
                                    except Exception as e:
                                        print(f"Error saving image: {e}")
                                    is_drawing_mode_active = False
                                    drawing_canvas = np.zeros((frame_height, frame_width, 3), np.uint8)
                                    cv2.putText(desktop_canvas, "DRAWING EXITED & SAVED", (NOTEPAD_X, frame_height - 60), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)

                                elif confirm_state == 'ENTER_DRAW':
                                    is_drawing_mode_active = True
                                    drawing_canvas = np.zeros((frame_height, frame_width, 3), np.uint8)
                                    cv2.putText(desktop_canvas, "ENTERING DRAWING MODE", (NOTEPAD_X, frame_height - 60), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 0), 2)
                                    
                                elif confirm_state == 'ENTER_KEYBOARD':
                                    keyboard_active = True
                                    is_drawing_mode_active = False
                                    cv2.putText(desktop_canvas, "ENTERING KEYBOARD MODE", (NOTEPAD_X, frame_height - 60), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 255), 2)

                            elif action_result == 'NO':
                                cv2.putText(desktop_canvas, "CANCELED.", (CONFIRM_BOX_X_CENTER - 100, CONFIRM_BOX_Y_CENTER + 80), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 0), 2)

                            # Always reset confirmation state variables after YES/NO action
                            confirm_state = None
                            confirm_hover_button = None
                            confirm_hover_start_time = 0
                            last_action_time = time.time()
                            
                    else:
                        # Reset hover if finger moved off buttons
                        confirm_hover_button = None
                        confirm_hover_start_time = 0
                
                # --- SET CONFIRMATION STATE LOGIC (Triggers) ---
                if confirm_state is None and time.time() - last_action_time > COOLDOWN_TIME:
                    
                    # 1. Thumbs Up Trigger (Exit Request for active modes)
                    if is_thumbs_up_trigger:
                        if keyboard_active:
                            confirm_state = 'EXIT_KEYBOARD'
                        elif is_drawing_mode_active:
                            confirm_state = 'EXIT_DRAW'
                        last_action_time = time.time()
                    
                    # --- Mode Switch Button Hover Logic (NEW ENTRY TRIGGERS) ---
                    
                    if not keyboard_active and not is_drawing_mode_active:
                        for btn in switch_buttons:
                            btn.draw(desktop_canvas)
                        
                        for btn in switch_buttons:
                            x, y = btn.pos
                            w, h = btn.size
                            
                            if x < ix < x + w and y < iy < y + h:
                                btn.draw(desktop_canvas, alpha=0.2) 

                                if hovered_button != btn:
                                    hovered_button = btn
                                    hover_start_time = time.time()
                                
                                hover_time = time.time() - hover_start_time
                                if hover_time > HOVER_DURATION:
                                    if btn.text == "KBD":
                                        confirm_state = 'ENTER_KEYBOARD'
                                    elif btn.text == "DRAW":
                                        confirm_state = 'ENTER_DRAW'
                                    last_action_time = time.time()
                                    hovered_button = None 
                                    break 
                        
                        if confirm_state is None:
                            is_hovering_switch_button = False
                            for btn in switch_buttons:
                                # FIX: Corrected typo 'BTB_H' to 'BTN_H'
                                if btn.pos[0] < ix < btn.pos[0] + BTN_W and btn.pos[1] < iy < btn.pos[1] + BTN_H:
                                    is_hovering_switch_button = True
                                    break
                            
                            if not is_hovering_switch_button:
                                hovered_button = None
                                hover_start_time = 0
                
            
            # --- 1. Drawing Mode Logic ---
            if is_drawing_mode_active:
                
                cv2.putText(desktop_canvas, "INDEX UP: Draw | 2 FINGERS UP: Save (Clears Canvas) | THUMBS UP: Exit (SAVES)", (NOTEPAD_X, frame_height - 20), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)

                is_drawing_pen = (len(lm_list) > 20) and is_index_extended and \
                                 (lm_list[12][1] > lm_list[10][1]) and is_ring_curled and is_pinky_curled
                
                if is_drawing_pen and confirm_state is None:
                    # Draw cursor on the desktop canvas
                    cv2.circle(desktop_canvas, (ix, iy), 10, DRAW_COLOR, cv2.FILLED)
                    if prev_draw_point is not None:
                        cv2.line(drawing_canvas, prev_draw_point, (ix, iy), DRAW_COLOR, DRAW_THICKNESS)
                    prev_draw_point = (ix, iy)
                else:
                    prev_draw_point = None

                is_two_finger_save_gesture = is_index_extended and is_middle_extended and is_ring_curled and is_pinky_curled

                if is_two_finger_save_gesture and confirm_state is None and time.time() - last_action_time > COOLDOWN_TIME:
                    file_path = f"drawing_{int(time.time())}.jpg"
                    try:
                        cv2.imwrite(file_path, drawing_canvas)
                        print(f"Drawing saved to {file_path}")
                        cv2.putText(desktop_canvas, f"DRAWING SAVED: {file_path}", (NOTEPAD_X, frame_height - 60), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
                    except Exception as e:
                        print(f"Error saving image: {e}")
                        cv2.putText(desktop_canvas, "ERROR SAVING DRAWING", (NOTEPAD_X, frame_height - 60), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)
                    
                    last_action_time = time.time()
                    drawing_canvas = np.zeros((frame_height, frame_width, 3), np.uint8) 

                # Apply the drawing canvas overlay to the desktop
                desktop_canvas = cv2.addWeighted(desktop_canvas, 1, drawing_canvas, 1.0, 0)
                
            # --- 2. Touchpad Mode Logic ---
            if not is_drawing_mode_active and not keyboard_active:
                
                cv2.putText(desktop_canvas, "INDEX+THUMB: Click | INDEX+THUMB SPREAD/PINCH: Zoom | INDEX+MIDDLE: Swipe", (NOTEPAD_X, frame_height - 20), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)

                # Map index finger position to screen coordinates
                screen_x = np.interp(ix, (frame_reduction, frame_width - frame_reduction), (0, screen_width))
                screen_y = np.interp(iy, (frame_reduction, frame_height - frame_reduction), (0, screen_height))
                
                # Apply smoothing
                curr_x = prev_x + (screen_x - prev_x) / smoothening
                curr_y = prev_y + (screen_y - prev_y) / smoothening
                pyautogui.moveTo(curr_x, curr_y)
                prev_x, prev_y = curr_x, curr_y
                
                # Draw a high-visibility cursor circle on the desktop canvas
                cv2.circle(desktop_canvas, (ix, iy), 10, (255, 255, 0), cv2.FILLED) 
                
                # --- Gesture Checks ---
                if len(lm_list) > 20: 
                    # a) Left Click Gesture: Index + Thumb Pinch
                    click_distance = math.hypot(tx - ix, ty - iy)

                    if click_distance < CLICK_DISTANCE and confirm_state is None:
                        cv2.circle(desktop_canvas, (ix, iy), 15, (0, 255, 255), cv2.FILLED) 
                        if time.time() - last_action_time > COOLDOWN_TIME:
                            pyautogui.click()
                            last_action_time = time.time()
                            time.sleep(0.1) 
                    
                    
                    # b) Zoom Gesture (Index + Thumb distance) - ROBUSTIFIED
                    is_thumb_index_zoom_pose = is_index_extended and is_ring_curled and is_pinky_curled

                    if is_thumb_index_zoom_pose and confirm_state is None and time.time() - last_action_time > 0.1: 
                        current_zoom_distance = math.hypot(ix - tx, iy - ty)
                        
                        if last_zoom_distance > 0:
                            delta_dist = current_zoom_distance - last_zoom_distance
                            
                            if delta_dist > ZOOM_THRESHOLD:
                                zoom_persistence_count += 1
                                zoom_type = '+'
                            elif delta_dist < -ZOOM_THRESHOLD:
                                zoom_persistence_count -= 1
                                zoom_type = '-'
                            else:
                                # Break if no significant movement
                                zoom_persistence_count = 0 

                            if zoom_persistence_count >= PERSISTENCE_FRAMES:
                                pyautogui.hotkey('ctrl', zoom_type) # Zoom In (Spread)
                                cv2.putText(desktop_canvas, f"ZOOM IN", (NOTEPAD_X, frame_height - 60), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 0), 3)
                                last_action_time = time.time()
                                zoom_persistence_count = 0 # Reset after action
                            elif zoom_persistence_count <= -PERSISTENCE_FRAMES:
                                pyautogui.hotkey('ctrl', zoom_type) # Zoom Out (Pinch)
                                cv2.putText(desktop_canvas, f"ZOOM OUT", (NOTEPAD_X, frame_height - 60), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 0), 3)
                                last_action_time = time.time()
                                zoom_persistence_count = 0 # Reset after action
                                
                        last_zoom_distance = current_zoom_distance
                    else:
                        last_zoom_distance = 0 # Reset tracking
                        zoom_persistence_count = 0
                        

                    # c) Swipe Gesture (Index + Middle extended, horizontal movement) - ROBUSTIFIED
                    is_swipe_gesture = is_index_extended and is_middle_extended and is_ring_curled and is_pinky_curled
                    
                    if is_swipe_gesture and confirm_state is None:
                        mid_x = (ix + (int(h1.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x * frame_width))) / 2
                        mid_y = (iy + (int(h1.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y * frame_height))) / 2
                        
                        if gesture_start_x is None:
                            gesture_start_x = mid_x
                            gesture_start_y = mid_y
                        else:
                            delta_x = mid_x - gesture_start_x
                            delta_y = mid_y - gesture_start_y # Track vertical stability

                            if abs(delta_y) < SLIDE_THRESHOLD / 2: # Check vertical stability
                                if delta_x > SLIDE_THRESHOLD:
                                    swipe_persistence_count += 1
                                    swipe_direction = 'right'
                                elif delta_x < -SLIDE_THRESHOLD:
                                    swipe_persistence_count -= 1
                                    swipe_direction = 'left'
                                else:
                                    swipe_persistence_count = 0
                                
                                # Trigger check
                                if swipe_persistence_count >= PERSISTENCE_FRAMES:
                                    pyautogui.hotkey('alt', swipe_direction)
                                    cv2.putText(desktop_canvas, f"SWIPE {swipe_direction.upper()}", (NOTEPAD_X, frame_height - 60), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 165, 0), 3)
                                    last_action_time = time.time()
                                    swipe_persistence_count = 0
                                    gesture_start_x = mid_x 
                                    gesture_start_y = mid_y
                                elif swipe_persistence_count <= -PERSISTENCE_FRAMES:
                                    pyautogui.hotkey('alt', swipe_direction)
                                    cv2.putText(desktop_canvas, f"SWIPE {swipe_direction.upper()}", (NOTEPAD_X, frame_height - 60), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 165, 0), 3)
                                    last_action_time = time.time()
                                    swipe_persistence_count = 0
                                    gesture_start_x = mid_x 
                                    gesture_start_y = mid_y

                            else:
                                swipe_persistence_count = 0
                                gesture_start_x = None
                                gesture_start_y = None
                                
                    else:
                        gesture_start_x = None 
                        gesture_start_y = None
                        swipe_persistence_count = 0
            
            # --- 3. Virtual Keyboard Logic (if active) ---
            if keyboard_active:
                finger_on_key = False
                
                for button in button_list:
                    button.draw(desktop_canvas)
                
                # NEW: Centered Feedback Box
                FEEDBACK_Y = NOTEPAD_Y - 80 # Position above the notepad
                FEEDBACK_WIDTH = 1000
                FEEDBACK_X = (frame_width - FEEDBACK_WIDTH) // 2

                cv2.rectangle(desktop_canvas, (FEEDBACK_X, FEEDBACK_Y), (FEEDBACK_X + FEEDBACK_WIDTH, FEEDBACK_Y + 60), (175, 0, 175), cv2.FILLED)
                cv2.putText(desktop_canvas, "Typing Feedback:", (FEEDBACK_X + 10, FEEDBACK_Y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(desktop_canvas, typed_text[-40:], (FEEDBACK_X + 10, FEEDBACK_Y + 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

                for button in button_list:
                    x, y = button.pos
                    w, h = button.size

                    if x < ix < x + w and y < iy < y + h and confirm_state is None:
                        finger_on_key = True
                        button.draw(desktop_canvas, alpha=0.2) 

                        if hovered_button != button:
                            hovered_button = button
                            hover_start_time = time.time()
                        
                        hover_time = time.time() - hover_start_time
                        if hover_time > HOVER_DURATION:
                            key_to_press = button.text
                            if key_to_press == "<-":
                                typed_text = typed_text[:-1]
                                pyautogui.press('backspace')
                            elif key_to_press == "Space":
                                typed_text += " "
                                pyautogui.press('space')
                            else:
                                typed_text += key_to_press
                                pyautogui.press(key_to_press.lower())

                            hovered_button = None 
                            hover_start_time = 0

                if not finger_on_key:
                    hovered_button = None
                    hover_start_time = 0
            
            # --- 4. Reset Gestures if hand is not detected or in keyboard mode ---
            else:
                last_zoom_distance = 0
                gesture_start_x = None
                zoom_persistence_count = 0
                swipe_persistence_count = 0

        # Display the final desktop hub canvas
        cv2.imshow("Virtual Controller", desktop_canvas)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # --- Cleanup ---
    cap.release()
    cv2.destroyAllWindows()
    hands.close()

if __name__ == "__main__":
    main()

