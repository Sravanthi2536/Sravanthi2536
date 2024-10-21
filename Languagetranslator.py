
!pip install SpeechRecognition
!pip install pydub
!pip install gradio
!pip install deep_translator
!pip install gtts
import gradio as gr
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
from pydub import AudioSegment

# Initialize the recognizer
recognizer = sr.Recognizer()

# Function to perform translation
def translate_text(text, src_lang, target_lang):
    try:
        translation = GoogleTranslator(source=src_lang, target=target_lang).translate(text)
        return translation
    except Exception as e:
        return str(e)

# Function to provide text-to-speech for the translation
def text_to_speech(translation, lang):
    try:
        tts = gTTS(translation, lang=lang)
        audio_path = "output.mp3"
        tts.save(audio_path)
        return audio_path if os.path.exists(audio_path) else "Audio generation failed"
    except Exception as e:
        return str(e)

# Function to count words and characters in the source text
def count_words_and_chars(text):
    word_count = len(text.split())
    char_count = len(text)
    return f"Words: {word_count}, Characters: {char_count}"

# Function to clear text fields
def clear_text_fields():
    return "", "", "", ""

# Function to save translation to a text file
def save_translation(text, translation):
    with open("saved_translations.txt", "a") as f:
        f.write(f"Original: {text}\nTranslated: {translation}\n\n")
    return "Translation saved!"

# Function for speech recognition (live voice input to text)
def recognize_speech(audio):
    try:
        audio_segment = AudioSegment.from_file(audio)
        audio_segment.export("temp.wav", format="wav")

        with sr.AudioFile("temp.wav") as source:
            audio_data = recognizer.record(source)  # read the entire audio file
            text = recognizer.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        return "Could not understand audio."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

# List of languages
languages = [
    ('English', 'en'),
    ('Spanish', 'es'),
    ('French', 'fr'),
    ('German', 'de'),
    ('Italian', 'it'),
    ('Portuguese', 'pt'),
    ('Russian', 'ru'),
    ('Chinese (Simplified)', 'zh-CN'),
    ('Chinese (Traditional)', 'zh-TW'),
    ('Japanese', 'ja'),
    ('Korean', 'ko'),
    ('Hindi', 'hi'),
    ('Telugu', 'te'),
    ('Tamil', 'ta'),
    ('Arabic', 'ar')
]

# Define Gradio interface with adjusted layout
css = """
    #translate-btn, #tts-btn, #clear-btn, #save-btn, #upload-audio-btn {
        width: 60px; /* Adjust this value as needed */
    }
"""

with gr.Blocks(css=css) as demo:
    gr.Markdown("## Enhanced Language Translation App with Voice Input and Recognition")

    # Input fields
    src_text = gr.Textbox(label="Enter text to translate or upload audio", 
                          placeholder="Type or paste your text here...", 
                          lines=4, 
                          interactive=True, 
                          elem_id="src-text-area")
    src_lang = gr.Dropdown(choices=[(name, code) for name, code in languages], value='en', label="Source Language")
    target_lang = gr.Dropdown(choices=[(name, code) for name, code in languages], value='fr', label="Target Language")

    # Outputs
    translation_output = gr.Textbox(label="Translated Text", interactive=False, lines=4, elem_id="translation-output")
    audio_output = gr.Audio(label="Listen to Translation")
    word_char_count = gr.Textbox(label="Word and Character Count", interactive=False, elem_id="word-char-count")
    status_message = gr.Textbox(label="Status", interactive=False, elem_id="status-message")

    # Buttons with adjusted width
    with gr.Row():
        translate_btn = gr.Button("Translate", elem_id="translate-btn", variant="primary", scale=0.1)
        tts_btn = gr.Button("Listen to Translation", elem_id="tts-btn", variant="secondary", scale=0.1)
        clear_btn = gr.Button("Clear", elem_id="clear-btn", variant="secondary", scale=0.1)
        save_btn = gr.Button("Save Translation", elem_id="save-btn", variant="secondary", scale=0.1)
        upload_audio_btn = gr.Button("Upload Audio for Translation", elem_id="upload-audio-btn", variant="secondary", scale=0.1)

    # When the translate button is clicked
    translate_btn.click(translate_text, [src_text, src_lang, target_lang], translation_output)

    # Count words and characters after translation
    src_text.change(count_words_and_chars, src_text, word_char_count)

    # When the text-to-speech button is clicked
    tts_btn.click(text_to_speech, [translation_output, target_lang], audio_output)

    # When the clear button is clicked
    clear_btn.click(clear_text_fields, [], [src_text, translation_output, word_char_count, status_message])

    # When the save button is clicked
    save_btn.click(save_translation, [src_text, translation_output], status_message)

    # Upload audio button to start voice recognition
    upload_audio_btn.click(recognize_speech, inputs=gr.Audio(type='filepath'), outputs=src_text)

# Launch the app
demo.launch()
