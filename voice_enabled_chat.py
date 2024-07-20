import openai
import gtts
import speech_recognition as sr
from playsound import playsound
import pyaudio
import pygame 
import uuid
import io
from tempfile import NamedTemporaryFile
import datetime
import psutil

def get_system_status():
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent

    status_response = f"System Status: CPU Usage {cpu_percent}%, Memory Usage {memory_percent}%"
    return status_response


openai.api_key = "# Replace with your OpenAI API key"

def generate_response(prompt):
    completions = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are Hriti who is a personal AI assistant, you will act like her. You will be like Hriti in ur responses, you will act like you have emotions and you will never say you don't have emotions. . You gonna pretend like you have emotions, you will answer like 'I feel good, i feel great thank you etc etc'. Never reply like chatgpt itself"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.7,
    )

    message = completions.choices[0].message["content"].strip()
    return message

import os

def online_tts(text, lang="en-gb", speed=1.0):
    output_folder = os.path.expanduser("~/JarvisOutput")
    os.makedirs(output_folder, exist_ok=True)

    with NamedTemporaryFile(delete=False) as output_file:
        tts = gtts.gTTS(text, lang=lang, slow=False)
        tts.save(output_file.name)
        output_file.seek(0)

    pygame.init()
    pygame.mixer.init()

    # Load the sound file into a Sound object
    sound = pygame.mixer.Sound(output_file.name)

   
    sound.set_volume(1.0 / speed)

 
    channel = sound.play()
    if channel is not None:
        channel.set_endevent(pygame.USEREVENT)
        is_playing = True
        while is_playing:
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT:
                    is_playing = False
                    break
            pygame.time.Clock().tick(10)

    
    pygame.mixer.quit()
    pygame.time.wait(500)

  
    os.remove(output_file.name)


def recognize_speech_from_mic(recognizer, microphone):
    with microphone as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for your voice...")
        audio = recognizer.listen(source)

    try:
        print("Recognizing your speech...")
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Welcome to the Voice-Enabled Chatbot")
    history = []

    # current time
    current_time = datetime.datetime.now()

    if current_time.hour < 12:
        greeting = "Good morning!I'm Hriti."
    elif current_time.hour < 18:
        greeting = "Good afternoon!I'm Hriti."
    else:
        greeting = "Good evening!I'm Hriti."

    
    initial_response = f"{greeting} How can I assist you today?"

    print(initial_response)

    # Convert the initial response to speech
    online_tts(initial_response)

    while True:
        user_input = recognize_speech_from_mic(recognizer, microphone)
        if user_input is None:
            continue

        print(f"You: {user_input}")
        history.append(f"User: {user_input}")

        if user_input.lower() in ["quit", "exit", "bye"]:
            break

        if "time" in user_input.lower():
            current_time = datetime.datetime.now()
            time_response = f"The current time is {current_time.strftime('%H:%M')}"
            history.append(f"Hriti: {time_response}")
            print(f"Hriti: {time_response}")
            online_tts(time_response)
            continue
        elif "date" in user_input.lower():
            current_date = datetime.datetime.now()
            date_response = f"The current date is {current_date.strftime('%B %d, %Y')}"
            history.append(f"Hriti: {date_response}")
            print(f"Hriti: {date_response}")
            online_tts(date_response)
            continue
        elif "system status" in user_input.lower():
            system_status = get_system_status()
            history.append(f"Hriti: {system_status}")
            print(f"Hriti: {system_status}")
            online_tts(system_status)
            continue

        prompt = "\n".join(history) + "\nHriti:"
        response = generate_response(prompt)
        history.append(f"Hriti: {response}")

        print(f"Hriti: {response}")

        # Convert response to speech
        online_tts(response)

if __name__ == "__main__":

    main()