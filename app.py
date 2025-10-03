import os
from gtts import gTTS
from googletrans import Translator
import PyPDF2
import re
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def extract_text_from_pdf(pdf_file):
    text = ""
    reader = PyPDF2.PdfReader(pdf_file)
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def create_pdf_from_text(text, target_lang):
    buffer = io.BytesIO()
    # Select font based on language
    if target_lang == 'hi':
        # For Hindi (Devanagari script)
        font_name = 'NotoSansDevanagari'
        font_file = 'NotoSansDevanagari-Regular.ttf'  # Place this file in your project directory
    else:
        # For most other languages
        font_name = 'DejaVu'
        font_file = 'DejaVuSans.ttf'  # Place this file in your project directory
    pdfmetrics.registerFont(TTFont(font_name, font_file))
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.setFont(font_name, 12)
    lines = text.split('\n')
    y = height - 40
    for line in lines:
        for subline in [line[i:i+100] for i in range(0, len(line), 100)]:
            c.drawString(40, y, subline)
            y -= 15
            if y < 40:
                c.showPage()
                c.setFont(font_name, 12)
                y = height - 40
    c.save()
    buffer.seek(0)
    return buffer

# Streamlit Web App
st.title("Multilingual Text-to-Speech App")

st.write("Upload a PDF or enter text, select a language, and get an audio file!")

input_type = st.radio("Choose input type:", ("Text", "PDF"))

text = ""
if input_type == "PDF":
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_file is not None:
        text = extract_text_from_pdf(uploaded_file)
        text = re.sub(r'\s+', ' ', text).strip()
        st.text_area("Extracted Text", text, height=200)
else:
    text = st.text_area("Enter text to convert to speech:", "", height=200)

# Language selection
languages = {
    'English': 'en',
    'French': 'fr',
    'Spanish': 'es',
    'German': 'de',
    'Hindi': 'hi',
    'Chinese': 'zh-cn',
    'Japanese': 'ja',
    'Russian': 'ru',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Arabic': 'ar',
    'Bengali': 'bn',
    'Korean': 'ko',
    'Turkish': 'tr',
    'Vietnamese': 'vi',
    'Urdu': 'ur',
    'Tamil': 'ta',
    'Telugu': 'te',
    'Gujarati': 'gu',
    'Marathi': 'mr',
    'Punjabi': 'pa',
}
language_name = st.selectbox("Select target language:", list(languages.keys()))
target_lang = languages[language_name]

if st.button("Convert to Speech/Translate"):
    if text.strip() == "":
        st.error("Please provide some text or upload a PDF.")
    else:
        translator = Translator()
        translated = translator.translate(text, dest=target_lang)
        translated_text = translated.text
        st.write(f"**Translated text:** {translated_text[:300]}{'...' if len(translated_text) > 300 else ''}")
        # Always generate audio
        tts = gTTS(text=translated_text, lang=target_lang)
        output_file = f"output_{target_lang}.mp3"
        tts.save(output_file)
        with open(output_file, 'rb') as f:
            audio_bytes = f.read()
        st.session_state['audio_bytes'] = audio_bytes
        st.session_state['audio_filename'] = output_file
        # If PDF input, also generate translated PDF
        if input_type == "PDF":
            pdf_buffer = create_pdf_from_text(translated_text, target_lang)
            st.session_state['pdf_bytes'] = pdf_buffer.getvalue()
            st.session_state['pdf_filename'] = f"translated_{target_lang}.pdf"

# Show download buttons if data exists in session_state
if 'audio_bytes' in st.session_state and 'audio_filename' in st.session_state:
    st.audio(st.session_state['audio_bytes'], format='audio/mp3')
    st.download_button(
        label="Download Audio",
        data=st.session_state['audio_bytes'],
        file_name=st.session_state['audio_filename'],
        mime="audio/mp3"
    )
if 'pdf_bytes' in st.session_state and 'pdf_filename' in st.session_state:
    st.download_button(
        label="Download Translated PDF",
        data=st.session_state['pdf_bytes'],
        file_name=st.session_state['pdf_filename'],
        mime="application/pdf"
    )

# CLI fallback (keep your previous CLI logic below if you want)
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        # CLI logic here (as before)
        pass