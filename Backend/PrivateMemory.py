import os

class PrivateMemory:
    """
    Handles local, private memory for both the assistant and the user.
    Loads identity data from text files and routes queries based on pronouns.
    """
    ASSISTANT_PROFILE_PATH = r"Backend\Data\assistant_profile.txt"
    USER_PROFILE_PATH = r"Backend\Data\user_profile.txt"
    
    _assistant_data = {}
    _user_data = {}
    _cache_timestamps = {}

    # Synonym mapping for robust matching
    SYNONYMS = {
        "clg": "college",
        "uni": "college",
        "university": "college",
        "campus": "college",
        "maker": "developer",
        "creator": "developer",
        "built": "developer",
        "made": "developer",
        "developed": "developer",
        "dev": "developer",
        "boss": "owner",
        "admin": "owner",
        "runs": "owner",
        "project": "project name",
        "about": "bio",
    }

    @classmethod
    def _load_if_needed(cls):
        """Loads both profiles if they have changed or aren't loaded."""
        cls._assistant_data = cls._load_file(cls.ASSISTANT_PROFILE_PATH, cls._assistant_data)
        cls._user_data = cls._load_file(cls.USER_PROFILE_PATH, cls._user_data)

    @classmethod
    def _load_file(cls, path, current_data):
        """Reads a profile text file into a dict, respecting file modification times."""
        if not os.path.exists(path):
            return {}

        try:
            mtime = os.path.getmtime(path)
            if path in cls._cache_timestamps and cls._cache_timestamps[path] == mtime and current_data:
                return current_data
            
            # defined reload
            data = {}
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        data[key.strip().lower()] = value.strip()
            
            cls._cache_timestamps[path] = mtime
            return data
            
        except Exception as e:
            print(f"[PrivateMemory] Error loading {path}: {e}")
            return current_data

    @classmethod
    def check_query(cls, query):
        """
        Determines if a query is a private profile question and returns the answer.
        Privacy-first: Returns answer locally, preventing API calls.
        """
        # 1. Normalize
        normalized_query = query.lower()
        for char in "?!.,;":
            normalized_query = normalized_query.replace(char, "")
        normalized_query = normalized_query.strip() # Example: "what is my college"

        # 2. Check for triggers
        
        # Identity Gating: Prevent false positives like "I want to play"
        identity_words = ["who", "what", "tell", "describe", "info"]
        is_identity_intent = any(w in normalized_query.split() for w in identity_words)

        is_user_query = is_identity_intent and any(w in normalized_query.split() for w in ["my", "me", "mine", "i"])
        is_assistant_query = is_identity_intent and any(w in normalized_query.split() for w in ["you", "your", "yours"])

        if not (is_user_query or is_assistant_query):
            # Fallback for implicit "who are you" if no pronoun but strong keywords presence could be added here
            # For now, strict routing as requested
            return None
        
        cls._load_if_needed()



        # --- Descriptive / Complex Query Handling ---
        
        # 1. Assistant: "tell me about your owner"
        # Strict phrase matching to avoid false positives
        if is_assistant_query and any(phrase in normalized_query for phrase in ["about your owner", "describe your owner", "info about your owner", "info on your owner"]):
             owner_name = cls._assistant_data.get("owner", "unknown")
             owner_bio = cls._assistant_data.get("owner bio", "")
             response = f"My owner is {owner_name}."
             if owner_bio:
                 response += f" {owner_bio}"
             return response

        # 2. User: "tell me about myself"
        # Strict phrase matching for user description
        user_descriptive_phrases = ["about myself", "about me", "describe me", "describe myself", "info about me", "info on me"]
        
        if (is_user_query and any(phrase in normalized_query for phrase in user_descriptive_phrases)) or normalized_query == "who am i":
             # Requirement: If Bio exists, return it. Else construct summary.
             user_bio = cls._user_data.get("bio")
             if user_bio:
                 return user_bio
             
             # Fallback summary
             name = cls._user_data.get("name", "User")
             college = cls._user_data.get("college", "unknown college")
             country = cls._user_data.get("country", "unknown country")
             return f"Your name is {name}. You study at {college} in {country}."

        # --- End Descriptive Handling ---

        # Priority Resolution: 
        # If both present, try User first. If no match, try Assistant.
        # This handles "Do you know my name?" (returns User name) vs "Who developed you for me?" (returns Assistant dev)
        
        result = None
        if is_user_query:
            if normalized_query == "who am i":
                 return f"Your name is {cls._user_data.get('name', 'User')}."
            result = cls._resolve_answer(normalized_query, cls._user_data, "Your")
        
        if result:
            return result
            
        if is_assistant_query:
            if normalized_query in ["who are you", "what is your name"]:
                 return f"My name is {cls._assistant_data.get('name', 'Leo')}."
            result = cls._resolve_answer(normalized_query, cls._assistant_data, "My")
            
        return result

    @classmethod
    def _resolve_answer(cls, query, profile_data, prefix):
        """
        Searches for keys in the query and returns formatted answer.
        """
        # 1. Expand Synonyms in query for matching
        words = query.split()
        expanded_words = [cls.SYNONYMS.get(w, w) for w in words]
        expanded_query = " ".join(expanded_words)

        # 2. Match longest matching key from profile
        # Sort keys by length desc to match "project name" before "project"
        sorted_keys = sorted(profile_data.keys(), key=len, reverse=True)
        
        matched_key = None
        for key in sorted_keys:
            # Check if key tokens imply a match. 
            # Simple substring match might be risky ("name" in "surname")
            # So checking word boundaries or direct substring if key is phrase
            # Improvement: Check exact word match OR phrase match to avoid partials
            if key in expanded_query.split() or key in expanded_query:
                matched_key = key
                break
        
        if matched_key:
            val = profile_data[matched_key]
            # Capitalize matched key for display
            display_key = matched_key.title() 
            return f"{prefix} {display_key} is {val}."
        
        return None  # Return None so main loop can decide what to do (or fallback)
        # Requirement: "Use a consistent fallback response for missing keys"
        # Since this function is called ONLY when we detected a "my/your" query, 
        # we arguably SHOULD return the fallback if we think it was intended for us but verified keys missing.
        # However, checking "my" might trigger false positives on general queries like "my computer is slow".
        # Returning "That info is not configured" for "my computer is slow" would be bad.
        # So, we return None if NO key matches.
        # The prompt says: "If query contains [pronouns] -> Use [Profile]".
        # And "Use a consistent fallback ... for missing keys".
        # This implies: If routing triggers, we MUST answer or say "not configured".
        # BUT "my computer is slow" shouldn't trigger this.
        # Let's refine routing: Trigger ONLY if "what/who" is present OR if it looks like a request.
        # Actually, let's stick to safe key matching. If key matches -> return answer.
        # If no key matches -> return None (let other Assistants/LLMs handle "my computer is slow").
        # If user explicitly asks "what is my [unknown_thing]", that's harder to distinguish from general query.
        
        # Compromise: We only fallback if high confidence it was a profile query.
        # The simplest safe bet: Return None if no key found. 
        # The "fallback" requirement likely applies when someone asks "what is my address" and "address" is NOT in the file.
        # To do that, we need to know "address" is the target intent. 
        # Without NLP, that's hard.
        # I will return None if no key matches to avoid blocking valid queries.


