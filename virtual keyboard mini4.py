import cv2
import mediapipe as mp
from time import sleep
from pynput.keyboard import Controller
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf")

# Initialize camera and mediapipe
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 1280)  # Set width
cap.set(4, 720)   # Set height

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)  # Track one hand for simplicity

keyboard_ctrl = Controller()

# Virtual keyboard layout
keys = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]
]

finalText = ""

# Button class
class Button:
    def __init__(self, position, key, size=(60, 60)):
        self.pos = position  # Position of the button
        self.key = key  # Key associated with the button
        self.size = size  # Size of the button (width, height)
        self.text = key  # Text is the key

# Create button list based on virtual keyboard layout
buttonList = []
button_size = (60, 60)
num_keys_in_row = len(keys[0])
keyboard_width = num_keys_in_row * button_size[0]
keyboard_height = len(keys) * button_size[1]

# Capture image width and height to center the keyboard
image_width = int(cap.get(3))
image_height = int(cap.get(4))

# Calculate the starting position to center the keyboard
start_x = (image_width - keyboard_width) // 2
start_y = (image_height - keyboard_height) // 2

# Create buttons and offset them for centering
for i, row in enumerate(keys):
    for j, key in enumerate(row):
        button_x = start_x + 60 * j  # Start X offset
        button_y = start_y + 60 * i  # Start Y offset
        buttonList.append(Button([button_x, button_y], key))

try:
    while True:
        success, img = cap.read()
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        # Check for hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get index fingertip position (landmark 8)
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                index_px = (int(index_tip.x * img.shape[1]), int(index_tip.y * img.shape[0]))

                # Iterate through all buttons to check if fingertip is over any button
                for button in buttonList:
                    x, y = button.pos
                    w, h = button.size

                    # Check if fingertip is within button area
                    if x < index_px[0] < x + w and y < index_px[1] < y + h:
                        # Highlight the button when finger is over it
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), cv2.FILLED)
                        cv2.putText(img, button.text, (x + 10, y + 40),
                                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

                        # Simulate key press if fingertip is close to the button
                        distance = abs(index_px[0] - x) + abs(index_px[1] - y)
                        if distance < 30:  # Adjust this threshold if needed
                            keyboard_ctrl.press(button.text)
                            finalText += button.text
                            sleep(0.25)  # Prevent multiple key presses due to high frame rate

        # Draw all the buttons (keyboard)
        for button in buttonList:
            x, y = button.pos
            w, h = button.size
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green borders
            cv2.putText(img, button.text, (x + 10, y + 40),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        # Display the text typed so far
        cv2.rectangle(img, (10, 550), (590, 690), (175, 0, 175), cv2.FILLED)
        cv2.putText(img, finalText, (20, 640),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

        cv2.imshow("Virtual Keyboard", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
