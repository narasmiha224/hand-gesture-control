import cv2
import mediapipe as mp
import time
import pyautogui

# Key mappings for left and right arrow keys
LEFT_ARROW = 'left'
RIGHT_ARROW = 'right'

def PressKey(key):
    pyautogui.keyDown(key)

def ReleaseKey(key):
    pyautogui.keyUp(key)


break_key_pressed = LEFT_ARROW
accelerato_key_pressed = RIGHT_ARROW

time.sleep(2.0)
current_key_pressed = set()

mp_draw = mp.solutions.drawing_utils
mp_hand = mp.solutions.hands

tipIds = [4, 8, 12, 16, 20]

video = cv2.VideoCapture(0)

with mp_hand.Hands(min_detection_confidence=0.5,
                   min_tracking_confidence=0.5) as hands:
    while True:
        keyPressed = False
        break_pressed = False
        accelerator_pressed = False
        key_count = 0
        key_pressed = None
        ret, image = video.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        lmList = []
        detected_text = "No hands detected"
        if results.multi_hand_landmarks:
            detected_text = "Hand detected"
            for hand_landmark in results.multi_hand_landmarks:
                myHands = results.multi_hand_landmarks[0]
                for id, lm in enumerate(myHands.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
                mp_draw.draw_landmarks(image, hand_landmark, mp_hand.HAND_CONNECTIONS)
                
        fingers = []
        if len(lmList) != 0:
            # Thumb (special case for left/right hand)
            if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
            # Other fingers
            for id in range(1, 5):
                if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            
            total = fingers.count(1)
            
            if total == 0:
                # Brake gesture detected (all fingers down)
                cv2.putText(image, "BRAKE", (45, 375), cv2.FONT_HERSHEY_SIMPLEX,
                            2, (0, 0, 255), 5)
                if break_key_pressed not in current_key_pressed:
                    PressKey(break_key_pressed)
                    current_key_pressed.add(break_key_pressed)
                # Release accelerator key if pressed
                if accelerato_key_pressed in current_key_pressed:
                    ReleaseKey(accelerato_key_pressed)
                    current_key_pressed.discard(accelerato_key_pressed)
                break_pressed = True
                key_pressed = break_key_pressed
                keyPressed = True
                key_count += 1
                
            elif total == 5:
                # Gas gesture detected (all fingers up)
                cv2.putText(image, "GAS", (45, 375), cv2.FONT_HERSHEY_SIMPLEX,
                            2, (0, 255, 0), 5)
                if accelerato_key_pressed not in current_key_pressed:
                    PressKey(accelerato_key_pressed)
                    current_key_pressed.add(accelerato_key_pressed)
                # Release brake key if pressed
                if break_key_pressed in current_key_pressed:
                    ReleaseKey(break_key_pressed)
                    current_key_pressed.discard(break_key_pressed)
                accelerator_pressed = True
                key_pressed = accelerato_key_pressed
                keyPressed = True
                key_count += 1
            else:
                # Partial finger states - no action, release any pressed keys
                if len(current_key_pressed) > 0:
                    for key in list(current_key_pressed):
                        ReleaseKey(key)
                    current_key_pressed.clear()
        else:
            # No hands detected - release any pressed keys
            if len(current_key_pressed) > 0:
                for key in list(current_key_pressed):
                    ReleaseKey(key)
                current_key_pressed.clear()

        # Show hand detection status on screen
        cv2.putText(image, detected_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 255, 255), 2)

        cv2.imshow("Automation Gestures", image)
        k = cv2.waitKey(1)
        if k == 27:  # ESC key to exit
            # Release all keys before exit
            for key in list(current_key_pressed):
                ReleaseKey(key)
            break

video.release()
cv2.destroyAllWindows()

