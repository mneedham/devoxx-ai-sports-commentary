import streamlit as st
from streamlit_modal import Modal
import pysondb
import datetime
import streamlit_float
import time
import jsonlines
import clickhouse_connect
from generate_commentary import call_llm

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

with jsonlines.open('data/1402.json') as reader:
    events = [row for row in reader]

events_by_game = []
game = []
for event in events:
    game.append(event)
    if event['point_score'] == 'FINISH':
        events_by_game.append(game)
        game = []

streamlit_float.float_init()


db = pysondb.db.getDb('data/livetext.json')

st.title("Live Text Commentary Admin Centre")

client = clickhouse_connect.get_client(host='localhost')

matches = client.query_df("""
select match_id, p1_name, p2_name
FROM matches
""")

match_id = st.selectbox(
    "Select match", 
    options=matches['match_id'],
    format_func=lambda x: f"{matches[matches.match_id == x]['p1_name'].values[0]} vs {matches[matches.match_id == x]['p2_name'].values[0]}"
)

st.write("***")

parameters = {'match_id': f"{match_id}"}

score_query = """
SELECT
    matches.* EXCEPT(match_id),
    latestPoint.previous_sets,
    set_score,
    point_score
FROM matches
LEFT JOIN
(
    SELECT *
    FROM points
    WHERE match_id = %(match_id)s
    ORDER BY id DESC
    LIMIT 1
) AS latestPoint ON latestPoint.match_id = matches.match_id
WHERE match_id = %(match_id)s
"""

score_result = client.query_df(score_query, parameters)

p1 = score_result.p1_name.values[0]
p2 = score_result.p2_name.values[0]

current_set = score_result.set_score.values[0]
sets = ", ".join(score_result.previous_sets.values[0] + [current_set])
details = f"{score_result.event_type.values[0]} {score_result.event_round.values[0]} "

st.write(f"""#### {p1} {sets or 'vs'} {p2}  
##### {details}
""")

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
            now = datetime.datetime.now().isoformat()
            db.add({'message': txt, 'datetime': now})
            st.toast(f"{now}: Your message was published", icon='😍')

popup = streamlit_float.float_dialog(
    st.session_state.show,
    background="#ADD8E6", 
    css="margin: 2rem 0 0;"
)
with popup:
    st.header("Generate message with AI")
    option = st.selectbox('Type of message',('Game summary', 'Set summary'))
    left, right, _ = st.columns([1,1,2], gap="small")
    with left:
        generate = st.button("Generate", disabled="ai_message" in st.session_state, key="run_button", type="primary")
    if generate:
        st.write("***")
        with st.spinner("Generating message"):
            latest_game = client.query_df(f"""
            SELECT points.* EXCEPT (match_id, id, publish_time)
            FROM points
            INNER JOIN
            (
                SELECT *
                FROM points
                WHERE (point_score = 'FINISH') AND (match_id = %(match_id)s)
                ORDER BY id DESC
                LIMIT 1
            ) AS latestPoint ON (latestPoint.set = points.set) AND (latestPoint.game = points.game)
            WHERE match_id = %(match_id)s
            ORDER BY id
            """, parameters)

            latest_events = [row.to_dict() for idx, row in latest_game.iterrows()]

            response = call_llm(latest_events, stream=False, model="gpt-3.5-turbo")
            message = response.choices[0].message.content

            st.session_state.ai_message = message
            st.rerun()

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