import json
import os
import re
from collections import deque
from datetime import datetime

class MemoryManager:
    """
    Manages Leo's memory systems:
    1. Short-Term Memory (STM): Last 10 interactions in RAM.
    2. Long-Term Memory (LTM): Explicit facts in Memory.json.
    3. Logs: Audit trail in ChatLog.json.
    """
    
    STM_LIMIT = 10
    MEMORY_FILE = r"Data\Memory.json"
    LOG_FILE = r"Data\ChatLog.json"
    
    # regex triggers for explicit memory encoding
    FACT_TRIGGERS = [
        r"(?i)\bmy name is\b",
        r"(?i)\bi am\b",
        r"(?i)\bi live in\b",
        r"(?i)\bi like\b",
        r"(?i)\bi love\b",
        r"(?i)\bi work as\b",
        r"(?i)\bmy job is\b"
    ]

    def __init__(self):
        self.stm = deque(maxlen=self.STM_LIMIT)
        self.ltm = self._load_ltm()
        self._hydrate_stm()

    # =========================
    # INTERNAL IO METHODS
    # =========================

    def _load_ltm(self):
        """Load LTM from JSON with safety check."""
        if not os.path.exists(self.MEMORY_FILE):
            return {"user_facts": [], "assistant_facts": []}
        
        try:
            with open(self.MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print("[Memory] Warning: Corrupt LTM. Starting fresh.")
            return {"user_facts": [], "assistant_facts": []}

    def _save_ltm(self):
        """Persist LTM to disk."""
        os.makedirs("Data", exist_ok=True)
        try:
            with open(self.MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.ltm, f, indent=4)
        except Exception as e:
            print(f"[Memory] Failed to save LTM: {e}")

    def _hydrate_stm(self):
        """Populate STM from the tail of ChatLog.json to maintain context on restart."""
        if not os.path.exists(self.LOG_FILE):
            return

        try:
            with open(self.LOG_FILE, 'r', encoding='utf-8') as f:
                # Load full log for now (optimization: seek later if file gets huge)
                # Since ChatLog is a JSON list, we load standard way
                logs = json.load(f)
                
                # Take last N valid entries
                # Filter out system messages if we only want conversation context
                # keeping system messages might be useful for errors, but LLM usually needs dialogue
                
                # We prioritize user/assistant messages for context
                context_logs = [entry for entry in logs if entry.get("role") in ["user", "assistant"]]
                
                for entry in context_logs[-self.STM_LIMIT:]:
                    self.stm.append(entry)
                    
        except Exception as e:
            print(f"[Memory] STM Hydration failed (starting empty): {e}")

    def _append_to_log(self, user_query, ai_response):
        """Append interaction to ChatLog.json (Audit Trail)."""
        current_log = []
        if os.path.exists(self.LOG_FILE):
            try:
                with open(self.LOG_FILE, 'r', encoding='utf-8') as f:
                    current_log = json.load(f)
            except:
                current_log = []
        
        current_log.append({"role": "user", "content": user_query})
        current_log.append({"role": "assistant", "content": ai_response})
        
        try:
            with open(self.LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(current_log, f, indent=4)
        except Exception as e:
            print(f"[Memory] Log write failed: {e}")

    # =========================
    # CORE LOGIC
    # =========================

    def get_context(self):
        """
        Returns the formatted context for the LLM.
        Format: [System+LTM] + [STM]
        """
        # 1. Enriched System Prompt
        user_facts = ", ".join(self.ltm.get("user_facts", []))
        assistant_facts = ", ".join(self.ltm.get("assistant_facts", []))
        
        enrichment = ""
        if user_facts:
            enrichment += f"\n[User Info: {user_facts}]"
        if assistant_facts:
            enrichment += f"\n[Self Info: {assistant_facts}]"
            
        # NOTE: The calling ChatBot will prepend the main System Prompt.
        # We return the enrichment string and the STM list.
        return enrichment, list(self.stm)

    def save_interaction(self, user_query, ai_response):
        """Save STM, LTM (if triggered), and Logs."""
        
        # 1. Update STM
        self.stm.append({"role": "user", "content": user_query})
        self.stm.append({"role": "assistant", "content": ai_response})
        
        # 2. Update Log (Audit)
        self._append_to_log(user_query, ai_response)
        
        # 3. Check LTM Triggers
        self._check_and_save_fact(user_query)

    def _check_and_save_fact(self, text):
        """Check if text contains a new fact and save it."""
        try:
            for pattern in self.FACT_TRIGGERS:
                if re.search(pattern, text):
                    # Dedup check
                    if text not in self.ltm["user_facts"]:
                        print(f"[Memory] New Fact Learned: {text}")
                        self.ltm["user_facts"].append(text)
                        self._save_ltm()
                    return # Save only one fact per turn to keep it simple
        except Exception as e:
            print(f"[Memory] Fact extraction error: {e}")
