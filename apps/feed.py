import streamlit as st
import pysondb
import datetime

db = pysondb.db.getDb('data/livetext.json')

st.title("Djokovic vs Shelton")

for doc in db.getAll()[::-1]:
    date_object = datetime.datetime.fromisoformat(doc['datetime'])

    st.write(f"""
    {date_object.strftime('%H:%M %B %d, %Y')}  
    {doc['message']} 
    """)