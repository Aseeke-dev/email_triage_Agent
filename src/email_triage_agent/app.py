import streamlit as st
from tools import fetch_unread_emails
from agent import process_live_email

st.set_page_config(page_title="Email Triage Agent", page_icon="📬", layout="centered")

st.title("📬 Personal Email Triage Agent")

if st.button("Triage Inbox (Top 5 Unread)", type="primary"):
    with st.spinner("Fetching live emails from Gmail..."):
        live_emails = fetch_unread_emails(max_results=5)
    
    if not live_emails:
        st.info("Your inbox is empty! No unread emails found.")
    
    else:
        with st.spinner("Agent is analyzing context and drafting replies..."):
            triage_results = process_live_email(live_emails)
    
    st.success("Triage Complete!")
    
    for res in triage_results:
        if res['category'] == 'urgent':
            icon = "🔴"
        elif res['category'] == 'follow-up':
            icon = "🟡"
        else:
            icon = "🟢"
        
        expander_title = f"{icon} {res['category'].upper()} ({res['urgency']}/5) - {res['subject']}"
        with st.expander(expander_title, expanded=(res['category'] == 'urgent')):
            st.write(f"**From:** {res['sender']}")
            
            if res['draft']:
                st.write("**Draft Reply:**")
                st.text_area("You can edit and copy your reply here:", value=res['draft'], height=100, key=res['id'])
            else:
                st.write("*No draft required for this category.*")
                
            