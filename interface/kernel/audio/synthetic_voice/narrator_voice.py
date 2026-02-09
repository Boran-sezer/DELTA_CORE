import re
import os
import soundfile as sf
import sounddevice as sd
from CONFIG import NARRATOR_VOICE, TEMP_OUTPUT_VOICE_PATH

# Import sécurisé pour éviter que l'erreur de syntaxe ne bloque DELTA
try:
    import comtypes
    import comtypes.client
    import pyttsx3
    comtypes.CoInitialize()
    COM_AVAILABLE = True
except Exception as e:
    COM_AVAILABLE = False
    print(f"Système vocal indisponible : {e}")

def split_text_and_code(text):
    if text is None: return []
    pattern = r'(```.*?```)'
    return re.split(pattern, text, flags=re.DOTALL)

def clean_text(text):
    return ''.join(char for char in text if char.isalnum() or char.isspace() or char in {'.', ',', '!', '?'})

class DELTAVoice:
    def __init__(self):
        self.engine = None
        if COM_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
            except Exception:
                self.engine = None
            
    def speak(self, text):
        if not self.engine: return

        segments = split_text_and_code(text)
        for segment in segments:
            if not segment.startswith('```'):
                clean_segment = clean_text(segment)
                if not clean_segment.strip(): continue

                os.makedirs(os.path.dirname(TEMP_OUTPUT_VOICE_PATH), exist_ok=True)
                
                if os.path.exists(TEMP_OUTPUT_VOICE_PATH):
                    try: os.remove(TEMP_OUTPUT_VOICE_PATH)
                    except: pass

                try:
                    self.engine.setProperty('voice', NARRATOR_VOICE)
                    self.engine.save_to_file(clean_segment, TEMP_OUTPUT_VOICE_PATH)
                    self.engine.runAndWait()

                    if os.path.exists(TEMP_OUTPUT_VOICE_PATH):
                        audio_data, samplerate = sf.read(TEMP_OUTPUT_VOICE_PATH, dtype='int16')
                        sd.play(audio_data, samplerate)
                        sd.wait()
                except Exception:
                    pass
                    