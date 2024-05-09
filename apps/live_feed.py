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
        event = json.loads(msg.data)
        title_display = f"##### {event['title']}" if event['title'] else ""
        st.info(f"""
        {title_display}
        _{event['datetime']}_  
        {event['score']}  \n
        {event['message']}
        """)

# import streamlit as st
# import json
# from sseclient import SSEClient

# print("Listening for updates...")
# if "messages" in st.session_state:
#     print("Closing old connection")
#     st.session_state["messages"].resp.close()

# url = "http://127.0.0.1:8000/livetext"
# st.session_state["messages"] = SSEClient(url)

# # Initialize an empty list to store messages
# if "message_list" not in st.session_state:
#     st.session_state.message_list = []

# placeholder = st.empty()

# with placeholder.container():
#     for msg in st.session_state["messages"]:
#         if msg.data:
#             # Prepend new message to the list
#             st.session_state.message_list.insert(0, json.loads(msg.data))
            
#             # Clear the previous display
#             placeholder.empty()
            
#             # Display all messages with the newest at the top
#             for message in st.session_state.message_list:
#                 st.write(message)
