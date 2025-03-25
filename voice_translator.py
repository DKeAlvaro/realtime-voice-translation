import asyncio
from google import genai
from dotenv import load_dotenv
import os
import speech_recognition as sr
from gtts import gTTS
import warnings
from pydub import AudioSegment
from pydub.playback import play

load_dotenv()
api_key=os.getenv("GEMINI_API_KEY") # Replace with your actual API key
warnings.filterwarnings('ignore')

LANGUAGES = {
    'arabic': 'ar',
    'farsi': 'fa',
    'tyrsenian': 'und',  
    'english': 'en',
    'dutch': 'nl',
    'spanish': 'es'
}

client = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})
model = "gemini-2.0-flash-exp"
config = {"response_modalities": ["TEXT"]}

async def translate_text(text, target_lang):
    prompt = f"ONLY RETURN THE FOLLOWING TEXT TRANSLATED TO {LANGUAGES[target_lang]}. DO NOT RETURN ANY OTHER THING {text}"
    async with client.aio.live.connect(model=model, config=config) as session:
        await session.send(input=prompt, end_of_turn=True)
        full_translation = ""
        async for response in session.receive():
            if response.text is not None:
                full_translation += response.text
        return full_translation.strip()

async def main():
    recognizer = sr.Recognizer()
    
    print("Available languages:")
    for i, lang in enumerate(LANGUAGES, 1):
        print(f"{i}. {lang}")
    
    lang_list = list(LANGUAGES.keys())
    input_lang_num = int(input("Select input language number: "))
    output_lang_num = int(input("Select output language number: "))
    input_lang = lang_list[input_lang_num - 1]
    output_lang = lang_list[output_lang_num - 1]
    
    if input_lang not in LANGUAGES or output_lang not in LANGUAGES:
        print("Invalid language selection")
        return
    
    while True:
        with sr.Microphone() as source:
            print("Speak now...")
            audio = recognizer.listen(source)
        
        try:
            text = recognizer.recognize_google(audio, language=LANGUAGES[input_lang])
            print(f"You said: {text}")
            
            translated_text = await translate_text(text, output_lang)
            print(f"Translation: {translated_text}")
            
            tts = gTTS(translated_text, lang=LANGUAGES[output_lang])
            tts.save("translation.mp3")
            audio = AudioSegment.from_file("translation.mp3")
            play(audio)
            duration = len(audio) / 1000  # Convert to seconds
            await asyncio.sleep(duration)
            os.remove("translation.mp3")

        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
        except sr.RequestError:
            print("API unavailable")

if __name__ == "__main__":
    asyncio.run(main())