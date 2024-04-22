import streamlit as st
import json
from sseclient import SSEClient

print("Listening for updates...")
if "messages" in st.session_state:
    print("Closing old connection")
    st.session_state["messages"].resp.close()

url = "http://127.0.0.1:8000/livetext"
st.session_state["messages"] = SSEClient(url)

placeholder = st.empty()

with placeholder.container():
  for msg in st.session_state["messages"]:
      if msg.data:
        st.write(json.loads(msg.data))