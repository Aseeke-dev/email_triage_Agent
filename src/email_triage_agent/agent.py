import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from schema import EmailTriageResult
from mock_data import MOCK_EMAILS

load_dotenv()

def build_triage_chain():
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    
    structured_llm = llm.with_structured_output(EmailTriageResult)
    
    prompt = ChatPromptTemplate.from_messages([("system", "You are an expert executive assistant. Triage the following email. If it is urgent, draft a brief, professional two-sentence reply."), ("human", "Sender: {sender}\nSubject: {subject}\nBody: {body}")])
    
    return prompt | structured_llm

def manual_test():
    print("Starting Phase 1 sandbox testing...")
    chain = build_triage_chain()
    
    for email in MOCK_EMAILS:
        print(f"processing: '{email['subject']}'...")
        result = chain.invoke({
            "sender": email["sender"],
            "subject": email["subject"],
            "body": email["body"]
        })
        print(f"Category: {result.category.upper()}")
        print(f"Urgency : {result.urgency_score}/5")
        if result.draft_reply:
            print(f"Draft   : {result.draft_reply}")
        print("-" * 50)
        
if __name__ == "__main__":
    manual_test()
    
    
# "gemini-3.5-flash-lite",  # Primary model
#             "gemini-3.5-flash",  # Fallback 1: Fast & highly available
#             "gemini-3.6-flash",    # Fallback 2: Higher reasoning capacity
#             "gemini-3.8-flash-lite"