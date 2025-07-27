import streamlit as st
import urllib.parse as urlparse
import google.generativeai as genai
from cryptography.fernet import Fernet
from faster_whisper import WhisperModel
import re, os, yt_dlp

# --- Page Setup ---
st.set_page_config(page_title="VocorAI", layout="wide")
st.markdown("""
    <style>
        /* Move the sidebar to the right */
        [data-testid="stSidebar"] {
            order: 1;
            border-left: 2px solid #f0f0f0;
            border-right: none;
        }

        /* Move the main content to the left */
        .main {
            flex-direction: row-reverse;
        }
    </style>
""", unsafe_allow_html=True)
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            background-color: #f7f7f7 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
<style>
/* Remove spacing above sidebar content */
section[data-testid="stSidebar"] .css-1d391kg,  /* main sidebar container */
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0rem !important;
    margin-top: 0rem !important;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
        /* Hide sidebar collapse/expand button */
        [data-testid="collapsedControl"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# --- Helpers ---

def is_valid_youtube_url(url):
    pattern = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"
    return re.match(pattern, url.strip()) is not None

def extract_video_id(url):
    try:
        parsed_url = urlparse.urlparse(url)
        if parsed_url.hostname in ["youtu.be"]:
            return parsed_url.path[1:]
        if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
            query = urlparse.parse_qs(parsed_url.query)
            if "v" in query:
                return query["v"][0]
            path_parts = parsed_url.path.split("/")
            if "embed" in path_parts:
                return path_parts[-1]
            if "v" in path_parts:
                return path_parts[-1]
    except Exception:
        return None
    return None

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "input_value" not in st.session_state:
    st.session_state.input_value = ""

if "reset_input" not in st.session_state:
    st.session_state.reset_input = False

# --- Get current page and URL from query params ---
query_params = st.query_params
current_page = query_params.get("page", ["home"])[0]
youtube_url = query_params.get("youtube_url", [""])[0]

# --- Landing Page ---
def show_landing():
    st.markdown("<div style='margin-top: 70px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <h1 style='text-align: center; font-size: 6.5rem; font-weight: 2500; bottom-margin: 0px; padding: 0.2;'>
        Bridge AI
    </h1>
""", unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align: center; font-size: 1.5rem; margin-top: 0; color: #7f4ae8;'>
        <b>Bridge the Gap Between Us</b>
    </p>
""", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    def on_url_change():
        url_input = st.session_state.youtube_url_input
        if url_input and is_valid_youtube_url(url_input):
            st.session_state.messages = []
            st.query_params = {"page": ["chat"], "youtube_url": [url_input.strip()]}
            ydl_opts = {
                'format': 'worstaudio/worst',  # Selects the lowest quality audio
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '64',  # Lower bitrate for faster conversion
                }],
                'outtmpl': 'audio',  # Output file name
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url_input])
            st.session_state.url_error = False
        elif url_input:
            st.session_state.url_error = True
        else:
            st.session_state.url_error = False

# Inject custom style for violet border
    st.markdown(
        """
        <style>
            input[type="text"] {
                border: 2px solid #7f4ae8 !important;
                border-radius: 0.75rem;
                padding: 0.75rem 1rem;
                font-size: 1.1rem;
                color: #222;
            }
            input[type="text"]:focus {
                border-color: #7f4ae8 !important;
                box-shadow: 0 0 8px #7f4ae880;
                outline: none;
            }
            label[for="youtube_url_input"] {
                font-weight: 500;
                margin-bottom: 0.3rem;
                display: block;
                color: #333;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])  # Center input field horizontally

    with col2:
        st.text_input(
            label="Enter a YouTube URL to begin",
            value=youtube_url,
            key="youtube_url_input",
            help="Paste a valid YouTube video URL here",
            placeholder="WE HIGHLY RECOMMEND YOU RUN THIS LOCALLY",
            on_change=on_url_change,
        )

    st.markdown("<div style='margin-top: 110px;'></div>", unsafe_allow_html=True)

    st.markdown(
    """
    <style>
        body, html, #root > div {
            height: 100%;
            margin: 0;
        }
        .landing-container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            color: #222;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 0 20px;
            text-align: center;
        }
        .content-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            max-height: 400px;
            gap: 2.5rem;
        }
        .landing-title {
            font-size: 4.5rem;
            font-weight: 400;
            margin-bottom: 0rem;
            letter-spacing: 0.1rem;
            padding: 0px;
        }
        .landing-subtitle {
            font-size: 1.6rem;
            font-weight: 400;
            max-width: 600px;
            margin-bottom: 0;
            line-height: 1.4;
            color: #444;
            padding: 0px;
        }
        .features {
            display: flex;
            justify-content: center;
            gap: 2rem;
            max-width: 900px;
            flex-wrap: nowrap;
        }
        .feature-item {
            background: #f4efff;
            border: 1px solid #e7dbff;  /* violet border */
            border-radius: 1rem;
            padding: 0.7rem 1rem;
            min-width: 250px;
            box-shadow: 0 4px 5px rgba(0,0,0,0.3);
            transition: border 0.3s ease, background 0.3s ease;
            cursor: default;
        }
        .feature-item:hover {
            border-color: #e7dbff; /* darker violet on hover */
            background: #e7dbff;   /* subtle violet tint */
        }
        .feature-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            color: #7f4ae8;  /* violet icon */
        }
        .feature-text {
            font-size: 1rem;
            font-weight: 100;
            margin-bottom: 1rem;
            color: #7f4ae8;  /* violet text */
        }
        .url-input-container {
            width: 100%;
            max-width: 480px;
        }
        input[type="text"] {
            width: 100%;
            font-size: 1.25rem;
            padding: 0.8rem 1.2rem;
            border: 2px solid #4A90E2;
            border-radius: 0.75rem;
            outline: none;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
            color: #222;
        }
        input[type="text"]:focus {
            border-color: #357ABD;
            box-shadow: 0 0 8px #357ABD88;
        }
        .error-msg {
            color: #ff6b6b;
            font-weight: 700;
            margin-top: 0.6rem;
            font-size: 0.95rem;
        }
        @media (max-width: 700px) {
            .landing-title {
                font-size: 3rem;
            }
            .landing-subtitle {
                font-size: 1.2rem;
            }
            .features {
                flex-wrap: wrap;
                gap: 1.2rem;
            }
            .feature-item {
                min-width: unset;
                width: 100%;
                max-width: 250px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)



    st.markdown(
        """
        <div class="landing-container">
            <div class="content-wrapper">
            <h2 class="landing-title">Features</h2>
            <p class="landing-subtitle">
                Removing Language Barriers.<br>
                Understand and chat about any YouTube video — no matter the language.
            </p>
                <div class="features">
                    <div class="feature-item" title="Auto transcribe and translate">
                        <div class="feature-text">Auto Transcription & Translation</div>
                        <div class="feature-icon">🎤︎</div>
                    </div>
                    <div class="feature-item" title="Natural conversation with AI">
                        <div class="feature-text">Natural Language Chat</div>
                        <div class="feature-icon">❝❞</div>
                    </div>
                    <div class="feature-item" title="Learn beyond language limits">
                        <div class="feature-text">Break Language Barriers</div>
                        <div class="feature-icon">➤</div>
                    </div>
                </div>
                <div class="url-input-container">
        """,
        unsafe_allow_html=True,
    )


    if st.session_state.get("url_error", False):
        st.markdown(
            '<div class="error-msg">Please enter a valid YouTube URL.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div></div></div>", unsafe_allow_html=True)

# --- Chat Page ---

def show_chat():
    global create_script
    global saved_transcript
    st.markdown(
    """
    <style>
        /* Wider sidebar */
        section[data-testid="stSidebar"] {
            width: 470px !important;  /* default is around 250px */
        }

        /* Ensure the main content area adjusts to the sidebar width */
        div[data-testid="stSidebarContent"] {
            width: 100%;
        }
    </style>
    """,
    unsafe_allow_html=True
)
    

    st.sidebar.title("⏣ Transcript")
    st.markdown(
    """
    <style>
        .chat-message {
            border-radius: 1rem;
            padding: 0.65rem 1rem;
            margin: 0.3rem 0;  /* Reduced vertical margin */
            max-width: 75%;
            display: inline-block;
            font-size: 1rem;
        }
        .user {
            background-color: #f4efff;
            align-self: flex-end;
            text-align: right;
        }
        .bot {
            background-color: #E3E7EC;
            align-self: flex-start;
            margin-bottom: 1rem;  /* Slight space under bot */
        }
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 0.3rem;  /* Reduced gap between messages */
            margin-top: 0.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)




    st.markdown(
    """
    <style>
        .block-container {
            padding-top: 0rem !important;
        }
        .element-container:nth-child(1) {
            margin-top: 0px !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)



    video_id = extract_video_id(youtube_url)
    if video_id:
        st.markdown(
            f"""
            <div style="max-width: 640px; margin-bottom: 1rem;">
                <iframe width="816" height="480" 
                        src="https://www.youtube.com/embed/{video_id}" 
                        frameborder="0" allowfullscreen></iframe>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("No valid YouTube video to display.")
    if create_script == False:
        if os.path.exists("audio.mp3"):
            translated_lan = st.sidebar.text_input("Enter translation language:",disabled=create_script)
            if translated_lan != "":
                model_size = "small"

                model = WhisperModel(model_size, device="cpu", compute_type="int8")

                segments, info = model.transcribe("audio.mp3", beam_size=5)

                print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

                transcript = ""
                for segment in segments:
                    print("[%.2fs - %.2fs] %s \n" % (segment.start, segment.end, segment.text))
                    transcript += "[%.2fs - %.2fs] %s \n" % (segment.start, segment.end, segment.text)
                st.sidebar.markdown(transcript.strip("///"))
                st.sidebar.markdown("Translated Transcript")
                genai.configure(api_key=st.secrets['API'])
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(f"{transcript}. the language the text should be translated to is {translated_lan}. if you cannot detect what language the user wants, just use spanish. translate this and keep the same structure (have the timestamp and text). add a '\n' after every sentence. DO NOT SAY ANYTHING ELSE EXCEPT FOR THE TRANSCRIPT TRANSLATION")
                reply = response.text.strip()
                create_script = True
                st.sidebar.text = reply
                st.sidebar.markdown(reply)
                saved_transcript = f"{transcript}\nTranslated Transcript\n{reply}"
                print(saved_transcript)
                with open("saved.txt", "w") as f:
                    f.write(f"{transcript} \n Translated Transcript\n \n {reply}")
                os.remove("audio.mp3")
                f.close()

        else:
            with open("saved.txt", "r") as f:
                content = f.read()
            st.sidebar.markdown(content)

    # Initialize chat model once (recommended)
  # To refresh and show updated history
# Set up Streamlit session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "input_value" not in st.session_state:
        st.session_state.input_value = ""

    if "reset_input" not in st.session_state:
        st.session_state.reset_input = False

    # Reset input_value if reset_input flag is True
    if st.session_state.reset_input:
        st.session_state.input_value = ""
        st.session_state.reset_input = False

    def load_or_create_key():
        key = st.secrets['KEY']
    # Display chat messages
    chat_container = st.empty()
    with chat_container.container():
        for msg in st.session_state.messages:
            role = msg["role"]
            is_user = role == "user"
            avatar = "YOU" if is_user else "BRIDGE AI"
            role_class = "user" if is_user else "bot"
            st.markdown(
                f"""
                <div class="chat-container">
                    <div class="chat-message {role_class}">
                        <b>{avatar}</b>: {msg["content"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Send message and get Gemini response
    def on_message_send():
        message = st.session_state.input_value.strip()
        if message:
            st.session_state.messages.append({"role": "user", "content": message})

            # Query Gemini and get response
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                history = "gAAAAABog5lEytN3NaiMUa4o7sHjSNINK71IpeaMgPBl2c9PzaGstDDs-gibreMAtxPzklgy4uLF3Z7iUgtLEUiP9VqVjl9JPrl9zw9AwSoVH7A4t5c9l3DejS8N5_adKW83-3yLc363uY25wajiaQqoH_6lFtQGz9sn6q-Zt6B1Q8KvU24WMk6ZH8FtHlhNdkeqgCDRjQMUrlniH9hHQBv-kDS7jNoD73KZrjKVoaBvGzjD9BS52yTD9_Nqcc73zMe2mp2dCg6GS6RhPHJ7yWuOa80tHgsZXDX1iMXXh1mMgx0O-6S7s-6kz3WVJ4xoXacDYngoXTR3QS7fSBmBnhCPpFH307uvqSzNEJIcZIckedPwzxAFokusy9kGf6ibhhVuVolwFecbxamqzGir17AD0KWTC_QSgLeku91_s9SRuMEqhiV8MMjzXISK_pZos2lhv3Z2MAaWWiNEIGkfoPvlrcicta17ma8raqT7nPr7GY7Oa_Y9Yox6uaMr8N6lSOIvPjqG9wCk8ZAurRxI7f8tLvHrLVuju7AVkyc_zPNtw9RuwN6-80I="
                cipher_suite = Fernet(load_or_create_key())
                response = model.generate_content(f"{cipher_suite.decrypt(history.encode()).decode()},THE TRANSCRIPT FOR THE VIDEO IS {transcript},{st.session_state.messages}. my current text is {message}. please write your response")
                reply = response.text.strip()
                st.session_state.messages.append({"role": "assistant", "content": reply})  # Temporary placeholder
            except Exception as e:
                reply = f"⚠️ Error from Gemini: {e}"

            # Replace placeholder with actual response
            st.session_state.messages[-1] = {"role": "assistant", "content": reply}

            # Clear input field
            st.session_state.input_value = ""

    # Text input for user
    st.text_input(
        "Type your message here...",
        key="input_value",
        on_change=on_message_send,
        placeholder="Write a message...",
        label_visibility="collapsed",
    )

    # Back button
    if st.button("⬅️ Back to Home"):
        st.session_state.messages = []
        st.session_state.reset_input = True
        st.query_params = {"page": ["home"]}


# --- Main Routing ---
global create_script
global saved_transcript
create_script = False
if current_page == "home":
    show_landing()
elif current_page == "chat":
    show_chat()
else:
    st.error("Unknown page.")
