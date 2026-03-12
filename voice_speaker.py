import pyttsx3

def speak(text):

    if not text:
        return

    try:
        engine = pyttsx3.init('sapi5')

        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)

        engine.setProperty('rate', 180)
        engine.setProperty('volume', 1.0)

        engine.say(text)
        engine.runAndWait()
        engine.stop()

    except Exception as e:
        print("Speech error:", e)