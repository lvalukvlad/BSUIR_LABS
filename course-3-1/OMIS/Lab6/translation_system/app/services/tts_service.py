import time

class TTSService:
    @staticmethod
    def synthesize(text):
        return f"/static/audio/{hash(text)}.mp3"