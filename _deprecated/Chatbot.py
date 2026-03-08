"""
DEPRECATED MODULE
This file is deprecated as of Backend Consolidation Phase 3.
All functionality has been migrated to:
- Backend/AnswerEngine.py (LLM logic)

DO NOT MODIFY THIS FILE.
It is kept for archival purposes and rollback safety.
"""
import json
import time
from dotenv import dotenv_values
from groq import Groq
from Backend.PrivateMemory import PrivateMemory
from Backend.FailureHandler import FailureHandler, DegradedMode
from Backend.StateManager import StateManager
from Backend.Memory import MemoryManager  # ✅ NEW MEMORY SYSTEM

# Load environment variables
env_vars = dotenv_values(".env")

Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Initialize Memory System
memory = MemoryManager()

# System prompt
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
*** IMPORTANT: If the user specifies a length constraint like "in two lines", "briefly", "in one sentence", "in three words", etc., you MUST strictly follow that constraint and keep your response within the specified length. ***
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

# Real-time info (simplified import or definition if not imported)
import datetime
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed:\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def ChatBot(Query):
    """
    Send the user's query to the chatbot and return the AI's response.
    Integrates Memory System (v1) for context and recording.
    """
    state = StateManager()
    
    # 1. Local Identity Check (Prioritized)
    local_response = PrivateMemory.check_query(Query)
    if local_response:
        # Save interaction to Memory (STM + Log)
        memory.save_interaction(Query, local_response)
        return local_response

    # 2. Check if we are in a mode that blocks cloud calls
    if state.GetDegradedMode() in [DegradedMode.LOCAL, DegradedMode.LOBOTOMIZED]:
        # We assume Main.py handles the UI feedback, but if ChatBot is called directly:
        msg = "I've lost my connection to the internet. I can only answer basic identity questions right now."
        return msg

    # 3. Cloud API Processing with Retry
    max_retries = 2
    for attempt in range(max_retries):
        try:
            # ✅ MEMORY READ: Get context from Memory System
            enrichment, stm_history = memory.get_context()
            
            # Construct Messages: System + [Enrichment] + Realtime + STM + Current User Query
            # Note: STM already contains recent history. We just need to append the NEW query for the API call 
            # (which hasn't been saved to STM yet).
            
            messages_payload = [
                {"role": "system", "content": System + enrichment},
                {"role": "system", "content": RealtimeInformation()}
            ] + stm_history + [{"role": "user", "content": float_query(Query)}]

            # Use updated model
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_payload,
                max_tokens=1024,
                temperature=0.7,
                top_p=1,
                stream=True,
                stop=None
            )

            Answer = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    Answer += chunk.choices[0].delta.content

            Answer = Answer.replace("</s>", "")
            Answer = AnswerModifier(Answer)

            # ✅ MEMORY WRITE: Save the successful interaction
            memory.save_interaction(Query, Answer)

            # Recovery: If successful, restore mode to FULL
            if state.GetDegradedMode() == DegradedMode.LIMITED:
                print("[ChatBot] Cloud restored, returning to FULL POWER.")
                state.SetDegradedMode(DegradedMode.FULL)

            return Answer

        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[ChatBot] Retry 1/1 after 1s due to: {e}")
                time.sleep(1)
                continue
            
            # All retries failed
            FailureHandler.handle_failure(e, context="ChatBot (Groq)")
            return "I'm having trouble connecting to my brain right now. Please check my API keys."

def float_query(q):
    return str(q)

# Run chatbot
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        response = ChatBot(user_input)
        print(response)
