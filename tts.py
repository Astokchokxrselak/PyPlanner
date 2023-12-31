import pyttsx3
from typing import *

VOLUME = 1


class MyEngine:
    def __init__(self, engine: pyttsx3.Engine):
        self.engine: pyttsx3.Engine = engine
        self.ran_once = False

    def isBusy(self):
        return self.ran_once and self.engine.isBusy()

    def say(self, text):
        self.engine.say(text)
        self.ran_once = True


engine = pyttsx3.init()
myEngine = MyEngine(engine)

"""
def engine():
    found_engine = None

    offset = 0
    for i in range(-1, -len(engines) - 1, -1):
        premade_engine = engines[i]
        if not premade_engine.isBusy():
            if found_engine is None:
                found_engine = premade_engine
            else:
                del engines[i]  # useless!

    if found_engine is None:
        found_engine = pyttsx3.init()
        engines.append(found_engine)

    if len(engines) == 0:
        new_engine = pyttsx3.init()
        engines.append(new_engine)
        return new_engine
    return engines[-1]
"""

voices = [r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0',
          r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0']


def waiting():
    return myEngine.isBusy()


def say(text, voiceIdx=0, speed=150):
    tts = myEngine
    try:
        tts.engine.endLoop()
    except RuntimeError:
        pass

    tts.engine.setProperty('voice', voices[voiceIdx])

    tts.engine.setProperty('volume', VOLUME)

    tts.engine.setProperty('rate', speed)

    tts.say(text)

    tts.engine.runAndWait()
    print("Done!")


if __name__ == "__main__":
    say("Hello World", 0)
    say("Hello World", 1)
