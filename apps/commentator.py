import streamlit as st
from streamlit_modal import Modal
import pysondb
import datetime
import streamlit_float
import time

st.markdown('''<style>
hr {
    background-color: #000000;
    margin:0; 
    border-bottom: 2px solid rgba(49, 51, 63, 0.2);
}
</style>''', unsafe_allow_html=True)

streamlit_float.float_init()

if "show" not in st.session_state:
    st.session_state.show = False

st.session_state.current_message = st.session_state.get('current_message', 'original')    

db = pysondb.db.getDb('data/livetext.json')

st.title("Live Text Commentary")

txt = st.text_area(
    "Next message",
    key="current_message",
    placeholder="Enter the next live text entry."
)

left, right = st.columns([21,3])

with left:
    generate_ai = st.button("Generate with AI", type="secondary")

if generate_ai:
    st.session_state.show = True
    st.experimental_rerun()

with right:
    if st.button('Publish', type="primary"):
        if not txt:
            st.error("No message provided")
        else:
            db.add({'message': txt, 'datetime': datetime.datetime.now().isoformat()})
            st.toast('Your message was published', icon='😍')

popup = streamlit_float.float_dialog(
    st.session_state.show,
    background="#FAFF69", 
    css="margin: 2rem 0 0;"
)
with popup:
    st.header("Generate message with AI")
    option = st.selectbox('Type of message',('Game summary', 'Set summary'))
    if st.button("Generate", disabled="ai_message" in st.session_state, key="run_button"):
        st.write("***")
        status = st.progress(0)
        for t in range(5):
            time.sleep(.1)
            status.progress(10*t+10)
        st.session_state.ai_message = 'Generated Message'
        st.rerun()

    if 'ai_message' in st.session_state:
        st.write("***")
        st.write(st.session_state.ai_message)

        left, right, _ = st.columns(3, gap="small")
        with left:
            def update_text(value):                     # <--- define callback function
                st.session_state.current_message = value
                del st.session_state['ai_message']
                st.session_state.show = False

            use_message = st.button("Use Message", key="use_message", type="primary", on_click=update_text, args=[st.session_state.ai_message])
                
        with right:
            if st.button("Discard", key="discard_message"):
                del st.session_state['ai_message']
                st.session_state.show = False
                st.rerun()