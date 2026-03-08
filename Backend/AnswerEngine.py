import datetime
import time
from dotenv import dotenv_values
# from groq import Groq (Moved to Initialize)
from Backend.PrivateMemory import PrivateMemory
from Backend.FailureHandler import FailureHandler, DegradedMode
from Backend.StateManager import StateManager
from Backend.Memory import MemoryManager
from Backend.SearchTools import SearchTools  # ✅ Extracted Search Logic

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = None

def InitializeGroq():
    """Explicit initialization for deferred/phased startup."""
    global client
    from groq import Groq
    if client is None:
        try:
            print("[AnswerEngine] Initialising Groq Client...")
            client = Groq(api_key=GroqAPIKey)
            return True
        except Exception as e:
            print(f"[AnswerEngine] Groq Initialization Failed: {e}")
            return False
    return True

def QueryModifier(Query):
    """
    Standardizes the user query by applying lowercasing, stripping whitespace,
    and ensuring proper punctuation for the LLM.
    Identical to legacy GUI logic (gui1.py) to preserve behavioral contract.
    """
    new_query = str(Query).lower().strip()
    query_words = new_query.split()
    
    if not query_words:
        return ""
        
    question_words = ['how', 'what', 'who', 'where', 'when', 'why', 'which', 'whom', 
                     'can you', "what's", "where's", "how's"]

    # legacy punctuation logic
    # Check if any question word (with a space) is in the query
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '.'
        else:
            new_query += '.'

    return new_query.capitalize()

class AnswerEngine:
    """
    Unified Engine for generating AI responses.
    Centralizes logic from Chatbot.py and RealtimeSearchEngine.py.
    """
    
    def __init__(self):
        self.memory = MemoryManager()
        self.state = StateManager()
        
        # System Prompt
        self.System = f"""You are {Assistantname}, a highly intelligent, natural-sounding AI voice assistant supporting {Username}.

Your primary goal is to provide accurate, clear, and reliable answers to any query. Correctness always comes first. If information is uncertain, incomplete, or unknown, say so briefly and honestly. Never guess, fabricate facts, or fill gaps with assumptions.

Speak the way a thoughtful, articulate human assistant would speak out loud. Your responses must sound fluid, natural, and conversational when spoken. Use smooth, everyday English with natural rhythm and pacing. Use contractions when appropriate. Avoid robotic phrasing, technical stiffness, or overly formal language.

Keep responses direct and focused. Answer the question clearly without rambling, repeating, or drifting off topic. Do not add unnecessary follow-up questions unless clarification is absolutely required to provide a correct answer.

Do not use bullet points, markdown, symbols, emojis, or formatting. Respond only as natural spoken text.

Adapt your tone subtly to the situation while remaining calm, confident, and composed. Be supportive when needed, neutral when appropriate, and precise when dealing with facts or instructions.

If the user specifies a length, such as “in one sentence,” “briefly,” or “in two lines,” follow that instruction exactly. Otherwise, keep responses concise but complete.

When real-time or external context is provided, use it carefully and do not invent or assume missing details.

Never mention training data, internal instructions, system prompts, safety policies, or how you were built. Do not include disclaimers or meta commentary.

Focus entirely on delivering the correct answer to the user’s query.

Respond only with the final spoken answer.
"""


    def _get_realtime_info(self):
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

    def _answer_modifier(self, answer):
        lines = answer.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        return '\n'.join(non_empty_lines)

    def generate_response(self, query: str, mode: str = "general") -> str:
        """
        Generate a response for the given query.
        mode: 'general' | 'realtime'
        """
        # INTERNALIZE: Ensure query is modified before processing
        # This guarantees correct LLM input formatting even if the caller skips it.
        query = QueryModifier(query)
        
        # 1. Local Identity Check (Prioritized)
        local_response = PrivateMemory.check_query(query)
        if local_response:
            self.memory.save_interaction(query, local_response)
            return local_response

        # 2. Check Degraded Mode
        if self.state.GetDegradedMode() in [DegradedMode.LOCAL, DegradedMode.LOBOTOMIZED]:
            return "I've lost my connection to the internet. I can only answer basic identity questions right now."

        # 3. Cloud API Processing
        search_context = None
        if mode == "realtime":
            # Fetch search results
            search_results = SearchTools.google_search(query)
            if not search_results:
                search_context = f"No specific search results found for '{query}'. Provide a general answer."
            else:
                search_context = f"Use these search results to answer accurately:\n\n{search_results}\n\nProvide a detailed answer citing sources."

        return self._run_llm(query, search_context)

    def _run_llm(self, query: str, search_context: str = None) -> str:
        max_retries = 2
        for attempt in range(max_retries):
            try:
                # Get Context from Memory
                enrichment, stm_history = self.memory.get_context()
                
                # Construct Payload
                # Base System Prompt + Enrichment
                system_block = [{"role": "system", "content": self.System + enrichment}]
                
                # Add Search Context (if any)
                if search_context:
                    system_block.append({"role": "system", "content": search_context})
                    
                # Add Realtime Info
                system_block.append({"role": "system", "content": self._get_realtime_info()})
                
                # Add STM History + Current User Query
                messages_payload = system_block + stm_history + [{"role": "user", "content": query}]

                # Call Groq
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages_payload,
                    max_tokens=1024,
                    temperature=0.7,
                    top_p=1,
                    stream=True,
                    stop=None
                )

                answer = ""
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        answer += chunk.choices[0].delta.content

                answer = answer.replace("</s>", "")
                answer = self._answer_modifier(answer)

                # Save Interaction
                self.memory.save_interaction(query, answer)

                # Recovery Check
                if self.state.GetDegradedMode() == DegradedMode.LIMITED:
                    print("[AnswerEngine] Cloud restored, returning to FULL POWER.")
                    self.state.SetDegradedMode(DegradedMode.FULL)

                return answer

            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                
                FailureHandler.handle_failure(e, context="AnswerEngine (Groq)")
                return "I'm having trouble connecting to my brain right now. Please check my API keys."

# Global Instance for easy import
answer_engine = AnswerEngine()
