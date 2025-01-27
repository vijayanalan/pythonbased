import speech_recognition as sr
import pyttsx3
import time
import bluetooth  # PyBluez library for Bluetooth
import RPi.GPIO as GPIO  # For GPIO control (if needed for physical devices)
import pyaudio

# Initialize pyttsx3 for speech
engine = pyttsx3.init()

# Setup GPIO (for Raspberry Pi only, optional)
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# If you're controlling physical devices, e.g., a light or fan with GPIO
DEVICE_PIN = 11  # Example GPIO pin for controlling something physical

GPIO.setup(DEVICE_PIN, GPIO.OUT)

# Bluetooth settings
# Replace with the Bluetooth address of your TV or Home Theater device
TV_BLUETOOTH_ADDR = "XX:XX:XX:XX:XX:XX"  # Bluetooth MAC address of your device

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Listening for command...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"Command received: {command}")
        return command
    except sr.UnknownValueError:
        speak("Sorry, I did not understand that.")
        return None
    except sr.RequestError:
        speak("Sorry, there is an issue with the speech service.")
        return None

def control_bluetooth_device(command):
    # Search for a Bluetooth service on the TV or Home Theater
    service_matches = bluetooth.find_service(address=TV_BLUETOOTH_ADDR)

    if service_matches:
        print(f"Found service on device: {TV_BLUETOOTH_ADDR}")
        first_match = service_matches[0]
        port = first_match["port"]
        name = first_match["name"]
        
        # Create a socket connection to the Bluetooth device
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((TV_BLUETOOTH_ADDR, port))

        if "turn on tv" in command:
            # Send a command to the Bluetooth device to turn on the TV (example command)
            sock.send("TURN_ON")  # Replace with the actual command your TV expects
            speak("Turning on the TV.")
        elif "turn off tv" in command:
            # Send a command to turn off the TV
            sock.send("TURN_OFF")  # Replace with the actual command your TV expects
            speak("Turning off the TV.")
        elif "volume up" in command:
            # Send a command to increase the volume (example)
            sock.send("VOLUME_UP")  # Replace with the actual command for volume up
            speak("Increasing the volume.")
        elif "volume down" in command:
            # Send a command to decrease the volume
            sock.send("VOLUME_DOWN")  # Replace with the actual command for volume down
            speak("Decreasing the volume.")
        elif "pause" in command:
            # Send a command to pause the media
            sock.send("PAUSE")  # Replace with actual command for pause
            speak("Pausing the media.")
        elif "play" in command:
            # Send a command to play media
            sock.send("PLAY")  # Replace with actual command for play
            speak("Playing the media.")
        else:
            speak("Sorry, I couldn't recognize the command.")
        
        # Close the Bluetooth connection after sending the command
        sock.close()
    else:
        speak("No Bluetooth service found on the TV or Home Theater.")

def main():
    speak("Voice control system activated. You can control your devices now.")
    
    while True:
        command = listen()
        if command:
            # Control Bluetooth devices (TV, Home Theater, etc.)
            control_bluetooth_device(command)
        
        # Example: Physical device control via GPIO
        if "turn on light" in command:
            GPIO.output(DEVICE_PIN, GPIO.HIGH)
            speak("The light is now ON.")
        elif "turn off light" in command:
            GPIO.output(DEVICE_PIN, GPIO.LOW)
            speak("The light is now OFF.")
        
        time.sleep(1)

if __name__ == "__main__":
    main()
