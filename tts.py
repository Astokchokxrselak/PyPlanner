import pyttsx3
from typing import *
import time

import asyncio

VOLUME = 1

voices = [r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0',
          r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0']


class TTS:
    class MyEngine:
        def __init__(self, engine: pyttsx3.Engine):
            self.engine: pyttsx3.Engine = engine
            self.ran_once = False

        def is_busy(self):
            return self.ran_once and self.engine.isBusy()

        def say(self, text):
            self.engine.say(text)
            self.ran_once = True

    def __init__(self, voice_idx):
        engine = pyttsx3.init()
        self.myEngine = TTS.MyEngine(engine)
        self.voice_idx = voice_idx

        self.myEngine.engine.setProperty('voice', voices[self.voice_idx])

        self.myEngine.engine.setProperty('volume', VOLUME)

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

    def set_voice(self, voice_idx):
        self.voice_idx = voice_idx

    def waiting(self):
        return self.myEngine.is_busy()

    def say(self, text, speed=150):
        tts = self.myEngine
        try:
            try:
                tts.engine.endLoop()
            except RuntimeError:
                pass

            tts.engine.setProperty('rate', speed)

            tts.say(text)

            tts.engine.runAndWait()
        except RuntimeError as r:
            print(r)
            time.sleep(3)
            self.say(text, speed)


if __name__ == "__main__":
    tts1 = TTS(0)
    tts2 = TTS(1)

