import streamlit as st
import re
import urllib.parse as urlparse
import google.generativeai as genai
from cryptography.fernet import Fernet


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
            placeholder="https://www.youtube.com/watch?v=example",
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
                        <div class="feature-text">some kind of shtty explanation about wtf this part is about and how the AI does this</div>
                    </div>
                    <div class="feature-item" title="Natural conversation with AI">
                        <div class="feature-text">Natural Language Chat</div>
                        <div class="feature-icon">❝❞</div>
                        <div class="feature-text">some kind of shtty explanation about wtf this part is about and how the AI does this</div>
                    </div>
                    <div class="feature-item" title="Learn beyond language limits">
                        <div class="feature-text">Break Language Barriers</div>
                        <div class="feature-icon">➤</div>
                        <div class="feature-text">some kind of shtty explanation about wtf this part is about and how the AI does this</div>
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
    


    
    st.sidebar.title("⏣ Translated Transcript")
    st.sidebar.markdown(
        """
    the accurate translation for this video, brought to you by **Bridge AI**.

    [0.00s - 7.40s]  Breaking news, Detroit rapper Eminem cancels his sold-out European tour to check himself
    [7.40s - 10.72s]  into rehab after admitting an addiction to sleep medication.
    [10.72s - 14.48s]  We'll have more on this story as it develops.
    [14.48s - 19.52s]  Shady Records recording artist Obi-Trice has apparently survived a gunshot to the head
    [19.52s - 23.72s]  in what appears to be a random drive-by shooting on Detroit's Lodge Freeway.
    [23.72s - 28.68s]  Meanwhile, Eminem is rumored to be remarrying his ex-wife and childhood sweetheart Kimberly
    [28.68s - 30.32s]  Mathers.
    [30.32s - 35.40s]  The on-and-off-again relationship with current wife Kim Mathers appears to be off again.
    [35.40s - 40.60s]  Just months after reconciling and remarrying, the rapper has filed for divorce for the second
    [40.60s - 43.80s]  time, ending their marriage once again.
    [43.80s - 47.88s]  Updating a story we brought you earlier about Gunfire and after Hours Club, we've learned
    [47.88s - 51.20s]  that the rapper Proof has been fatally shot.
    [51.20s - 55.80s]  Proof's real name is Deshaun Hulton, longtime best friend of Eminem and a member of the
    [55.80s - 56.80s]  rap group D-12.
    [56.80s - 81.80s]  Police say they're still trying to figure out the motive for the shooting.
    [81.80s - 88.60s]  So this is it, this is what I wish for, just isn't how I envisioned it, famed to the point
    [88.60s - 89.60s]  of imprisonment.
    [89.60s - 93.80s]  I just thought that should it be different, but something changed the minute that I got
    [93.80s - 94.80s]  a whip of it.
    [94.80s - 99.60s]  I started to inhale it, smell it, started sniffing it, and it became my cocaine.
    [99.60s - 104.04s]  I just couldn't quit, I just wanted a little bit, then it turned me to a monster.
    [104.04s - 107.24s]  I became a hypocrite, concert after concert.
    [107.24s - 112.72s]  I was raking in the door, rolling in green, had the game hemmed up like a sewing machine.
    [112.72s - 117.40s]  But I was losing my freedom, there was no one for me, to not go and be seen, it's just
    [117.40s - 118.40s]  going to be me.
    [118.40s - 123.08s]  And there was no one between, you're either love that I hated, every CD, critics gave it
    [123.08s - 124.08s]  a three than three.
    [124.08s - 129.48s]  Years later they go back and re-rated, and call it Slim Shady LP, the greatest, the
    [129.48s - 134.52s]  Marshall Mathers was the classic, Eminem show was fantastic, but I'm gorgeous, didn't
    [134.52s - 136.24s]  have the caliber to match it.
    [136.24s - 141.08s]  I guess enough time just ain't past yet, a couple more years, that shit'll be ill-matic
    [141.08s - 146.76s]  and eight years later I'm still at it, divorce, remarried, a felon, a father, sleeping pill
    [146.76s - 151.96s]  addict, and this is real talk, I feel like the incredible Hulk, my back has been broken,
    [151.96s - 152.96s]  I can still hold.
    [152.96s - 157.68s]  So be careful what you wish for, cause you just might get it, and if you get it then
    [157.68s - 162.68s]  you just might not know what to do with it, cause it might just come back on you
    [162.68s - 163.68s]  tenfold.
    [163.68s - 181.24s]  I gotta let it from a fan set, he's been praying for me, every day and for some reason it's
    [181.24s - 186.24s]  been weighing on my mind heavy, cause I don't read every letter I get, but something told
    [186.24s - 190.24s]  me to go ahead and open it, but why would someone pray for you when they don't know
    [190.24s - 191.24s]  you?
    [191.24s - 195.80s]  I pray for me when I was local, and as I lay these vocals, I think of all the shit I had
    [195.80s - 200.64s]  to go through, just to get to where I'm at, I've already told you at least a thousand times
    [200.64s - 205.24s]  in these rhymes, I appreciate the prayer, but I've already got, got on my side, and it's
    [205.24s - 210.40s]  been one hell of a ride hasn't it, just watching it from an opposite standpoint, man, boy
    [210.40s - 215.96s]  it's got to look nuts, and it's the only word I can think of right now, one half
    [215.96s - 220.36s]  to describe this shit, it's just like a vibe you get, go ahead and pop to it, just

End of transcript
    """
    )
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
    genai.configure(api_key=secrets['API'])
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
        key_file = "secret.key"    
        with open(key_file, "rb") as f:
            key = f.read()
        return key
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
                response = model.generate_content(f"{cipher_suite.decrypt(history.encode()).decode()},{st.session_state.messages}. my current text is {message}. please write your response")
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
if current_page == "home":
    show_landing()
elif current_page == "chat":
    show_chat()
else:
    st.error("Unknown page.")
