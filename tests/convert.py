import streamlit as st
import urllib.parse
import webbrowser

st.set_page_config(page_title="Google Search", layout="wide")

# Center using HTML and style it
st.markdown("""
    <style>
        .centered-box {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }

        input[type="text"] {
            font-size: 18px !important;
            padding: 0.4em 0.8em !important;
        }

        .stButton button {
            font-size: 16px;
            padding: 0.4em 1em;
            margin-top: 1em;
        }
    </style>
    <div class="centered-box">
        <h2>🔍 Google Search</h2>
    </div>
""", unsafe_allow_html=True)

# Streamlit elements injected into centered box
placeholder = st.empty()

with placeholder.container():
    st.markdown("<div style='height: 36vh'></div>", unsafe_allow_html=True)

    query = st.text_input("", placeholder="Search Google...")

    if query:
        encoded_query = urllib.parse.quote_plus(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        st.markdown(f"<p style='text-align: center'><a href='{search_url}' target='_blank'>Click here to search on Google</a></p>", unsafe_allow_html=True)

        if st.button("Open in Browser"):
            webbrowser.open_new_tab(search_url)
