# Backend/LLM.py - Unified LLM Router with Offline Support
# ========================================================
#
# This module routes LLM requests between:
# 1. Cloud LLM (Groq) - Fast, primary
# 2. Local LLM (Ollama) - Works offline
#
# Configuration (via .env):
# - LLM_MODE: "hybrid", "cloud", or "local"
# - OLLAMA_URL: Ollama server URL
# - OLLAMA_MODEL: Model name (e.g., "mistral:7b", "llama3.1:8b")
# - OFFLINE_MODE: Force local-only operation

import os
import time
from typing import Optional, Generator
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")

# Configuration
LLM_MODE = env_vars.get("LLM_MODE", "hybrid")
OLLAMA_URL = env_vars.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = env_vars.get("OLLAMA_MODEL", "mistral:7b")
OFFLINE_MODE = env_vars.get("OFFLINE_MODE", "false").lower() == "true"


class LLMError(Exception):
    """Custom exception for LLM errors"""
    pass


def is_ollama_available() -> bool:
    """Check if Ollama server is running"""
    try:
        import requests
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_available_models() -> list:
    """Get list of available Ollama models"""
    if not is_ollama_available():
        return []
    
    try:
        import requests
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [m["name"] for m in data.get("models", [])]
    except:
        pass
    return []


def generate(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    stream: bool = False,
    history: Optional[list] = None,
    model_override: Optional[str] = None
) -> dict:
    """
    Unified LLM generation function.
    
    Args:
        prompt: User prompt
        system_prompt: System instruction
        temperature: Sampling temperature
        max_tokens: Max tokens to generate
        stream: Enable streaming response
        history: Chat history as list of {"role": "...", "content": "..."}
        model_override: Override default model
        
    Returns:
        dict with keys:
        - text: Generated text
        - source: "cloud" or "local"
        - model: Model used
        - duration: Generation time
    """
    mode = LLM_MODE
    
    # Check offline mode
    if OFFLINE_MODE:
        mode = "local"
    
    # Route based on mode
    if mode == "local":
        return _generate_local(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            history=history,
            model=model_override
        )
    elif mode == "cloud":
        return _generate_cloud(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            history=history
        )
    elif mode == "hybrid":
        # Try cloud first, fall back to local
        try:
            return _generate_cloud(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                history=history
            )
        except Exception as e:
            print(f"[LLM] Cloud LLM failed: {e}, trying local...")
            try:
                return _generate_local(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                    history=history,
                    model=model_override
                )
            except Exception as e2:
                raise LLMError(f"All LLM methods failed. Cloud: {e}, Local: {e2}")
    else:
        raise LLMError(f"Unknown LLM mode: {mode}")


def _generate_local(
    prompt: str,
    system_prompt: Optional[str],
    temperature: float,
    max_tokens: int,
    stream: bool,
    history: Optional[list],
    model: Optional[str]
) -> dict:
    """Generate using local Ollama"""
    if not is_ollama_available():
        raise LLMError("Ollama server not available")
    
    try:
        import requests
        
        model_name = model or OLLAMA_MODEL
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})
        
        # Make request
        start_time = time.time()
        
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        if stream:
            # Handle streaming
            response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json=payload,
                stream=True,
                timeout=120
            )
            
            full_text = ""
            for line in response.iter_lines():
                if line:
                    import json
                    data = json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        full_text += data["message"]["content"]
            
            duration = time.time() - start_time
            
            return {
                "text": full_text,
                "source": "local",
                "model": model_name,
                "duration": duration
            }
        else:
            response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json=payload,
                timeout=120
            )
            
            if response.status_code != 200:
                raise LLMError(f"Ollama error: {response.text}")
            
            data = response.json()
            duration = time.time() - start_time
            
            return {
                "text": data.get("message", {}).get("content", ""),
                "source": "local",
                "model": model_name,
                "duration": duration
            }
            
    except ImportError:
        raise LLMError("requests not installed")
    except Exception as e:
        raise LLMError(f"Local LLM failed: {e}")


def _generate_cloud(
    prompt: str,
    system_prompt: Optional[str],
    temperature: float,
    max_tokens: int,
    stream: bool,
    history: Optional[list]
) -> dict:
    """Generate using cloud Groq"""
    try:
        from groq import Groq
        
        # Get API key
        api_key = env_vars.get("GroqAPIKey")
        if not api_key:
            raise LLMError("GroqAPIKey not configured")
        
        client = Groq(api_key=api_key)
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})
        
        # Make request
        start_time = time.time()
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            stream=stream,
            stop=None
        )
        
        if stream:
            full_text = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_text += chunk.choices[0].delta.content
            
            duration = time.time() - start_time
            
            return {
                "text": full_text,
                "source": "cloud",
                "model": "llama-3.3-70b-versatile",
                "duration": duration
            }
        else:
            text = completion.choices[0].message.content
            duration = time.time() - start_time
            
            return {
                "text": text,
                "source": "cloud",
                "model": "llama-3.3-70b-versatile",
                "duration": duration
            }
            
    except ImportError:
        raise LLMError("groq not installed")
    except Exception as e:
        raise LLMError(f"Cloud LLM failed: {e}")


def pull_model(model_name: str) -> bool:
    """
    Pull a model from Ollama registry.
    Note: This downloads the model locally (can be several GBs)
    """
    if not is_ollama_available():
        print("[LLM] Ollama not available")
        return False
    
    try:
        import requests
        import json
        
        print(f"[LLM] Pulling model: {model_name}")
        print("[LLM] This may take several minutes...")
        
        response = requests.post(
            f"{OLLAMA_URL}/api/pull",
            json={"name": model_name},
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "status" in data:
                    print(f"[LLM] {data['status']}")
                if data.get("completed", False):
                    print(f"[LLM] Model pulled successfully!")
                    return True
        
        return True
        
    except Exception as e:
        print(f"[LLM] Failed to pull model: {e}")
        return False


def get_llm_info() -> dict:
    """Get current LLM configuration info"""
    return {
        "mode": LLM_MODE,
        "ollama_url": OLLAMA_URL,
        "ollama_model": OLLAMA_MODEL,
        "offline_mode": OFFLINE_MODE,
        "ollama_available": is_ollama_available(),
        "available_models": get_available_models()
    }


# Legacy function for backward compatibility with AnswerEngine
def chat_completion(
    messages: list,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    stream: bool = False
) -> dict:
    """
    Legacy function for AnswerEngine compatibility.
    """
    # Extract prompt and system from messages
    system_prompt = None
    user_prompt = None
    history = []
    
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        if role == "system":
            system_prompt = content
        elif role == "user":
            user_prompt = content
        elif role == "assistant":
            history.append({"role": "assistant", "content": content})
        else:
            history.append({"role": role, "content": content})
    
    # Add user message to history
    if user_prompt:
        history.append({"role": "user", "content": user_prompt})
    
    result = generate(
        prompt=user_prompt or "",
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream,
        history=history[:-1] if history else None
    )
    
    # Format for AnswerEngine compatibility
    return {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": result["text"]
            }
        }]
    }


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("LLM Router - Test Mode")
    print("=" * 60)
    
    print(f"\nCurrent Configuration:")
    info = get_llm_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Options:")
    print("  1. Test cloud LLM (Groq)")
    print("  2. Test local LLM (Ollama)")
    print("  3. Test hybrid mode")
    print("  4. Pull Ollama model")
    print("  5. Check Ollama availability")
    print("=" * 60)
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        result = _generate_cloud(
            prompt="What is Python?",
            system_prompt="You are a helpful assistant.",
            temperature=0.7,
            max_tokens=100,
            stream=False,
            history=None
        )
        print(f"\nResult: {result['text']}")
        print(f"Source: {result['source']}")
        print(f"Duration: {result['duration']:.2f}s")
        
    elif choice == "2":
        result = _generate_local(
            prompt="What is Python?",
            system_prompt="You are a helpful assistant.",
            temperature=0.7,
            max_tokens=100,
            stream=False,
            history=None,
            model=None
        )
        print(f"\nResult: {result['text']}")
        print(f"Source: {result['source']}")
        print(f"Duration: {result['duration']:.2f}s")
        
    elif choice == "3":
        result = generate(
            prompt="What is Python?",
            system_prompt="You are a helpful assistant.",
            temperature=0.7,
            max_tokens=100
        )
        print(f"\nResult: {result['text']}")
        print(f"Source: {result['source']}")
        print(f"Duration: {result['duration']:.2f}s")
        
    elif choice == "4":
        model = input("Enter model name (e.g., mistral:7b): ").strip()
        if model:
            pull_model(model)
        else:
            print("No model specified")
            
    elif choice == "5":
        print(f"\nOllama available: {is_ollama_available()}")
        print(f"Available models: {get_available_models()}")
        
    else:
        print("Invalid choice")
