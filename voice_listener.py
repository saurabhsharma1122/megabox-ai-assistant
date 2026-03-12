import speech_recognition as sr
import time

recognizer = sr.Recognizer()


def listen():

    try:
        with sr.Microphone() as source:

            recognizer.adjust_for_ambient_noise(source, duration=0.3)

            audio = recognizer.listen(
                source,
                timeout=1,
                phrase_time_limit=6
            )

        try:
            text = recognizer.recognize_google(audio)
            return text

        except sr.UnknownValueError:
            return None

        except sr.RequestError:
            return None

    except sr.WaitTimeoutError:
        return None

    except Exception:
        time.sleep(0.5)
        return None