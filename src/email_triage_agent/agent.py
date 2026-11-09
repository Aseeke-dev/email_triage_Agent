import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from schema import TriageDescision
from mock_data import MOCK_EMAILS
from prompts import TRIAGE_PROMPT, DRAFTING_PROMPT

load_dotenv()

def process_live_email(email_list):
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

    
    triage_chain = TRIAGE_PROMPT | llm.with_structured_output(TriageDescision)
    drafting_chain = DRAFTING_PROMPT | llm | StrOutputParser()
    
    final_results = []
    
    for email in email_list:
        
        body_snippet = email["body"][:200]
        decision = triage_chain.invoke({
            "sender": email["sender"],
            "subject": email["subject"],
            "body_snippet": body_snippet
        })
        
        draft = ""
        if decision.category == "urgent":
            print("   -> Urgent email detected. Drafting reply...")
            draft = drafting_chain.invoke({
                "sender": email["sender"],
                "subject": email["subject"],
                "body": email["body"]
            })
            
        final_results.append({
            "id": email["id"],
            "sender": email["sender"],
            "subject": email["subject"],
            "category": decision.category,
            "urgency": decision.urgency_score,
            "draft": draft
        })
        
    return final_results
    
    
# "gemini-3.5-flash-lite",  # Primary model
#             "gemini-3.5-flash",  # Fallback 1: Fast & highly available
#             "gemini-3.6-flash",    # Fallback 2: Higher reasoning capacity
#             "gemini-3.8-flash-lite"