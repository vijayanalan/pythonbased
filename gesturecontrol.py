import cv2
import mediapipe as mp
import pyttsx3
import bluetooth
import RPi.GPIO as GPIO
import time

# Initialize pyttsx3 for speech
engine = pyttsx3.init()

# Setup GPIO (for Raspberry Pi only, optional)
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# GPIO pins for controlling connected devices (e.g., Light, Fan, TV)
DEVICE_PIN = 11  # Example pin for a light or fan

GPIO.setup(DEVICE_PIN, GPIO.OUT)

# Bluetooth settings for TV/Home Theater (replace with your device's MAC address)
TV_BLUETOOTH_ADDR = "XX:XX:XX:XX:XX:XX"  # Bluetooth MAC address of your device

# Initialize MediaPipe for hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Initialize camera
cap = cv2.VideoCapture(0)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def control_device(command):
    if "turn on light" in command:
        GPIO.output(DEVICE_PIN, GPIO.HIGH)  # Turn on light
        speak("Turning on the light.")
    elif "turn off light" in command:
        GPIO.output(DEVICE_PIN, GPIO.LOW)  # Turn off light
        speak("Turning off the light.")
    elif "turn on tv" in command:
        control_bluetooth_device("TURN_ON")
        speak("Turning on the TV.")
    elif "turn off tv" in command:
        control_bluetooth_device("TURN_OFF")
        speak("Turning off the TV.")
    elif "volume up" in command:
        control_bluetooth_device("VOLUME_UP")
        speak("Increasing the volume.")
    elif "volume down" in command:
        control_bluetooth_device("VOLUME_DOWN")
        speak("Decreasing the volume.")
    else:
        speak("Sorry, I couldn't recognize the command.")

def control_bluetooth_device(command):
    service_matches = bluetooth.find_service(address=TV_BLUETOOTH_ADDR)
    if service_matches:
        print(f"Found service on device: {TV_BLUETOOTH_ADDR}")
        first_match = service_matches[0]
        port = first_match["port"]
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((TV_BLUETOOTH_ADDR, port))

        sock.send(command)  # Send the gesture-based command (e.g., "TURN_ON")
        sock.close()
    else:
        speak("No Bluetooth service found.")

def detect_gesture(frame):
    # Convert the frame to RGB (mediapipe requires RGB format)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Gesture Recognition (using simple gesture - e.g., fist, open hand, etc.)
            if is_fist(hand_landmarks):
                speak("Fist detected. Turning off the light.")
                control_device("turn off light")
            elif is_open_hand(hand_landmarks):
                speak("Open hand detected. Turning on the light.")
                control_device("turn on light")
            elif is_thumb_up(hand_landmarks):
                speak("Thumb up detected. Increasing volume.")
                control_device("volume up")
            elif is_thumb_down(hand_landmarks):
                speak("Thumb down detected. Decreasing volume.")
                control_device("volume down")
                
    return frame

def is_fist(hand_landmarks):
    # Check if fingers are closed (fist gesture)
    finger_ids = [4, 8, 12, 16, 20]
    fist = True
    for finger in finger_ids:
        if hand_landmarks.landmark[finger].y > hand_landmarks.landmark[0].y:
            fist = False
            break
    return fist

def is_open_hand(hand_landmarks):
    # Check if fingers are open (open hand gesture)
    finger_ids = [4, 8, 12, 16, 20]
    open_hand = True
    for finger in finger_ids:
        if hand_landmarks.landmark[finger].y < hand_landmarks.landmark[0].y:
            open_hand = False
            break
    return open_hand

def is_thumb_up(hand_landmarks):
    # Check if thumb is raised (thumb up gesture)
    return hand_landmarks.landmark[4].y < hand_landmarks.landmark[3].y

def is_thumb_down(hand_landmarks):
    # Check if thumb is pointing down (thumb down gesture)
    return hand_landmarks.landmark[4].y > hand_landmarks.landmark[3].y

def main():
    speak("Gesture control system activated.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = detect_gesture(frame)
        
        # Display the resulting frame
        cv2.imshow("Gesture Control", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
