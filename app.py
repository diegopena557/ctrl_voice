import os
import time
import json
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import paho.mqtt.client as paho
from gtts import gTTS
from googletrans import Translator

# ==============================
# CONFIGURACIÓN DE LA PÁGINA
# ==============================
st.set_page_config(
    page_title="Interfaz Multimodal",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ==============================
# ESTILOS PERSONALIZADOS
# ==============================
st.markdown("""
    <style>
    body {
        background-color: #f5f7fa;
    }
    .main {
        background: linear-gradient(180deg, #ffffff 0%, #f7f9fc 100%);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 0 25px rgba(0,0,0,0.08);
    }
    h1 {
        color: #1E3A8A;
        text-align: center;
        font-size: 2.4em !important;
    }
    h2, h3 {
        color: #2563EB;
    }
    .stButton>button {
        background-color: #2563EB;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 10em;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #1E40AF;
        transform: scale(1.05);
    }
    .stImage>img {
        border-radius: 15px;
        box-shadow: 0 0 15px rgba(0,0,0,0.15);
    }
    </style>
""", unsafe_allow_html=True)

# ==============================
# FUNCIONES
# ==============================
def on_publish(client, userdata, result):
    print("✅ Dato publicado con éxito\n")

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.success(f"📩 Mensaje recibido: {message_received}")

# Inicialización MQTT
broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("GIT-HUBC")
client1.on_message = on_message

# ==============================
# INTERFAZ PRINCIPAL
# ==============================
st.title("🎙️ INTERFACES MULTIMODALES")
st.subheader("✨ Control por Voz con MQTT y Traducción")

image = Image.open('lildog.jpg')
st.image(image, width=250, caption="Asistente Virtual")

st.markdown("#### 🗣️ Da clic en el botón y habla para enviar comandos")

stt_button = Button(label="🎤 Iniciar Voz", width=200)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# ==============================
# PROCESAMIENTO DE VOZ
# ==============================
if result and "GET_TEXT" in result:
    texto = result.get("GET_TEXT").strip()
    st.info(f"🗨️ Has dicho: **{texto}**")

    with st.spinner("🤔 Interesante... veamos qué dice..."):
        time.sleep(1.5)

    # Envío por MQTT
    client1.on_publish = on_publish
    client1.connect(broker, port)
    message = json.dumps({"Act1": texto})
    client1.publish("voice_ctrl", message)

    # Traducción automática
    translator = Translator()
    traduccion = translator.translate(texto, dest='en').text
    st.success(f"🌍 Traducción (EN): {traduccion}")

    # Generar audio con gTTS
    tts = gTTS(text="Interesante, veamos qué dice", lang="es")
    audio_path = "temp_audio.mp3"
    tts.save(audio_path)
    st.audio(audio_path)

# ==============================
# PIE DE PÁGINA
# ==============================
st.markdown("""
<hr>
<p style='text-align:center; color:gray; font-size:0.9em'>
Desarrollado con ❤️ usando Streamlit + MQTT + Google Translate + gTTS
</p>
""", unsafe_allow_html=True)

