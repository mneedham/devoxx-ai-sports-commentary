import streamlit as st
from streamlit_modal import Modal
import datetime
import streamlit_float
import time
import jsonlines
import clickhouse_connect
from generate_commentary import call_llm
import queries
from kafka import KafkaProducer
import json

client = clickhouse_connect.get_client(host='localhost')
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=str.encode
)

if "show" not in st.session_state:
    st.session_state.show = False
st.session_state.current_message = st.session_state.get('current_message', '')

st.markdown('''<style>
hr {
    background-color: #000000;
    margin:0; 
    border-bottom: 2px solid rgba(49, 51, 63, 0.2);
}
</style>''', unsafe_allow_html=True)

streamlit_float.float_init()

st.title("Live Text Commentary Admin Centre")

matches = client.query_df(queries.matches_query)

match_id = st.selectbox(
    "Select match", 
    options=matches['match_id'],
    format_func=lambda x: f"{matches[matches.match_id == x]['p1_name'].values[0]} vs {matches[matches.match_id == x]['p2_name'].values[0]}"
)
parameters = {'match_id': f"{match_id}"}

st.write("***")

score_result = client.query_df(queries.score_query, parameters)

def extract_score(score_result):
    p1 = score_result.p1_name.values[0]
    p2 = score_result.p2_name.values[0]

    current_set = score_result.set_score.values[0]
    sets = ", ".join(score_result.previous_sets.values[0] + [current_set])
    score = f"{p1} {sets or 'vs'} {p2}"
    return sets, score

sets, score = extract_score(score_result)
details = f"{score_result.event_type.values[0]} {score_result.event_round.values[0]} "

st.write(f"""#### Match Score
**{score}**  
{details}
""")

st.write("#### Live Text Entry")
title = st.text_input('Message title', placeholder="Optional title for live text entry.")
txt = st.text_area(
    "Next message",
    key="current_message",
    placeholder="Enter the next live text entry."
)

left, right = st.columns([21,3])
if sets:
    with left:
        generate_ai = st.button("Generate with AI", type="secondary")

    if generate_ai:
        st.session_state.show = True
        st.rerun()

with right:
    if st.button('Publish', type="primary"):
        if not txt:
            st.error("No message provided")
        else:
            now = datetime.datetime.now().isoformat()
            event = {'match_id': match_id, 'score': score, 'title': title, 'message': txt, 'datetime': now}
            producer.send(topic="livetext", key=event['match_id'], value=event)
            producer.flush()
            st.toast(f"{now}: Your message was published", icon='😍')

if sets:
    popup = streamlit_float.float_dialog(
        st.session_state.show,
        background="#ADD8E6", 
        css="margin: 2rem 0 0;"
    )
    with popup:
        st.header("Generate message with AI")
        option = st.selectbox('Type of message',('Last Game summary', 'Last 5 minutes'))
        left, right, _ = st.columns([1,1,2], gap="small")
        with left:
            generate = st.button("Generate", disabled="ai_message" in st.session_state, key="run_button", type="primary")
        if generate:
            st.write("***")
            with st.spinner("Generating message"):
                if option == "Last Game summary":
                    query_response = client.query_df(queries.latest_game_query, parameters)
                elif option == "Last 5 minutes":
                    query_response = client.query_df(queries.recent_query, parameters)

                latest_events = [row.to_dict() for idx, row in query_response.iterrows()]

                if latest_events:
                    response = call_llm(latest_events, stream=False, model="gpt-3.5-turbo")
                    message = response.choices[0].message.content
                    st.session_state.ai_message = message
                    st.rerun()

                else:
                    st.error("No events found")
        with right:
            if st.button("Close", key="close_message"):
                st.session_state.show = False
                st.rerun()

        if 'ai_message' in st.session_state:
            st.write("***")
            st.write(st.session_state.ai_message)

            left, right, _ = st.columns(3, gap="small")
            with left:
                def update_text(value):
                    st.session_state.current_message = value
                    del st.session_state['ai_message']
                    st.session_state.show = False

                use_message = st.button("Use Message", key="use_message", type="primary", on_click=update_text, args=[st.session_state.ai_message])
                    
            with right:
                if st.button("Discard", key="discard_message"):
                    del st.session_state['ai_message']
                    st.session_state.show = False
                    st.rerun()