import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
from datetime import datetime
import json
import os

class JarvisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JARVIS - AI Assistant")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0a1128")
        
        # Message queue for thread-safe GUI updates
        self.message_queue = queue.Queue()
        
        # Conversation history
        self.conversation_history = []
        
        # Status
        self.is_listening = False
        self.is_processing = False
        
        self.setup_styles()
        self.create_widgets()
        self.process_queue()
        
    def setup_styles(self):
        """Configure custom styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        bg_color = "#0a1128"
        fg_color = "#00d9ff"
        accent_color = "#a855f7"
        
        style.configure("Custom.TFrame", background=bg_color)
        style.configure("Custom.TLabel", background=bg_color, foreground=fg_color, font=("Arial", 10))
        style.configure("Title.TLabel", background=bg_color, foreground=fg_color, font=("Arial", 24, "bold"))
        style.configure("Status.TLabel", background=bg_color, foreground="#fbbf24", font=("Arial", 9))
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container
        main_frame = ttk.Frame(self.root, style="Custom.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ===== HEADER =====
        header_frame = ttk.Frame(main_frame, style="Custom.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame, text="⚡ JARVIS", style="Title.TLabel")
        title_label.pack(side=tk.LEFT)
        
        # Status indicator
        self.status_label = ttk.Label(header_frame, text="● Ready", style="Status.TLabel")
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # Time
        self.time_label = ttk.Label(header_frame, text="", style="Custom.TLabel")
        self.time_label.pack(side=tk.RIGHT, padx=10)
        self.update_time()
        
        # ===== MAIN CONTENT AREA =====
        content_frame = ttk.Frame(main_frame, style="Custom.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left Panel - Chat Area
        left_panel = ttk.Frame(content_frame, style="Custom.TFrame")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Chat display
        chat_frame = tk.Frame(left_panel, bg="#1a1f3a", relief=tk.RIDGE, bd=2)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            bg="#1a1f3a",
            fg="#00d9ff",
            font=("Consolas", 11),
            insertbackground="#00d9ff",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure text tags for styling
        self.chat_display.tag_config("user", foreground="#a855f7", font=("Consolas", 11, "bold"))
        self.chat_display.tag_config("jarvis", foreground="#00d9ff", font=("Consolas", 11))
        self.chat_display.tag_config("system", foreground="#fbbf24", font=("Consolas", 9, "italic"))
        self.chat_display.tag_config("error", foreground="#ef4444", font=("Consolas", 10))
        self.chat_display.tag_config("timestamp", foreground="#6b7280", font=("Consolas", 8))
        
        # Input area
        input_frame = tk.Frame(left_panel, bg="#1a1f3a", relief=tk.RIDGE, bd=2)
        input_frame.pack(fill=tk.X)
        
        self.input_field = tk.Text(
            input_frame,
            height=3,
            wrap=tk.WORD,
            bg="#1a1f3a",
            fg="#ffffff",
            font=("Consolas", 11),
            insertbackground="#00d9ff",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.input_field.bind("<Return>", self.on_enter_key)
        self.input_field.bind("<Shift-Return>", lambda e: None)  # Allow Shift+Enter for newline
        
        # Right Panel - Controls & Info
        right_panel = ttk.Frame(content_frame, style="Custom.TFrame", width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_panel.pack_propagate(False)
        
        # Voice Control Section
        voice_frame = tk.LabelFrame(
            right_panel,
            text="Voice Control",
            bg="#1a1f3a",
            fg="#00d9ff",
            font=("Arial", 12, "bold"),
            relief=tk.RIDGE,
            bd=2
        )
        voice_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.voice_button = tk.Button(
            voice_frame,
            text="🎤 Start Listening",
            command=self.toggle_voice,
            bg="#a855f7",
            fg="white",
            font=("Arial", 12, "bold"),
            relief=tk.RAISED,
            bd=3,
            padx=20,
            pady=15,
            cursor="hand2"
        )
        self.voice_button.pack(pady=15, padx=15, fill=tk.X)
        
        # Quick Actions Section
        actions_frame = tk.LabelFrame(
            right_panel,
            text="Quick Actions",
            bg="#1a1f3a",
            fg="#00d9ff",
            font=("Arial", 12, "bold"),
            relief=tk.RIDGE,
            bd=2
        )
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        actions = [
            ("📝 Clear Chat", self.clear_chat),
            ("💾 Save History", self.save_history),
            ("📊 Show Stats", self.show_stats),
            ("⚙️ Settings", self.open_settings),
        ]
        
        for text, command in actions:
            btn = tk.Button(
                actions_frame,
                text=text,
                command=command,
                bg="#1f2937",
                fg="#00d9ff",
                font=("Arial", 10),
                relief=tk.FLAT,
                bd=0,
                padx=10,
                pady=8,
                cursor="hand2",
                anchor="w"
            )
            btn.pack(fill=tk.X, padx=10, pady=3)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#374151"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1f2937"))
        
        # System Info Section
        info_frame = tk.LabelFrame(
            right_panel,
            text="System Info",
            bg="#1a1f3a",
            fg="#00d9ff",
            font=("Arial", 12, "bold"),
            relief=tk.RIDGE,
            bd=2
        )
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.info_text = tk.Text(
            info_frame,
            wrap=tk.WORD,
            bg="#1a1f3a",
            fg="#6b7280",
            font=("Consolas", 9),
            relief=tk.FLAT,
            padx=10,
            pady=10,
            height=10
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.config(state=tk.DISABLED)
        self.update_system_info()
        
        # Bottom bar with Send button
        bottom_frame = ttk.Frame(main_frame, style="Custom.TFrame")
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.send_button = tk.Button(
            bottom_frame,
            text="Send Message ➤",
            command=self.send_message,
            bg="#00d9ff",
            fg="#0a1128",
            font=("Arial", 12, "bold"),
            relief=tk.RAISED,
            bd=3,
            padx=30,
            pady=10,
            cursor="hand2"
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Welcome message
        self.add_message("JARVIS", "Hello! I'm JARVIS, your AI assistant. How can I help you today?", "system")
        
    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%I:%M %p")
        self.time_label.config(text=f"🕐 {current_time}")
        self.root.after(1000, self.update_time)
        
    def update_system_info(self):
        """Update system information display"""
        info = f"""Messages: {len(self.conversation_history)}
Voice: {"Active" if self.is_listening else "Inactive"}
Processing: {"Yes" if self.is_processing else "No"}

Capabilities:
• Natural Language Processing
• Voice Recognition
• Web Search
• Task Automation
• File Management
• System Control
"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)
        
    def add_message(self, sender, message, tag="jarvis"):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add timestamp
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add sender
        if sender == "You":
            self.chat_display.insert(tk.END, f"{sender}: ", "user")
        elif sender == "JARVIS":
            self.chat_display.insert(tk.END, f"{sender}: ", "jarvis")
        else:
            self.chat_display.insert(tk.END, f"{sender}: ", "system")
        
        # Add message
        self.chat_display.insert(tk.END, f"{message}\n\n", tag)
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Save to history
        self.conversation_history.append({
            "timestamp": timestamp,
            "sender": sender,
            "message": message
        })
        
        self.update_system_info()
        
    def send_message(self):
        """Send a message from input field"""
        message = self.input_field.get(1.0, tk.END).strip()
        
        if not message:
            return
            
        # Clear input field
        self.input_field.delete(1.0, tk.END)
        
        # Add user message
        self.add_message("You", message, "user")
        
        # Update status
        self.status_label.config(text="● Processing...")
        self.is_processing = True
        
        # Process in background thread
        threading.Thread(target=self.process_message, args=(message,), daemon=True).start()
        
    def process_message(self, message):
        """Process the message (placeholder for actual AI logic)"""
        # Simulate processing
        import time
        time.sleep(1)
        
        # Placeholder response - integrate your actual Jarvis logic here
        response = f"I received your message: '{message}'. This is where you'll integrate your AI response logic."
        
        # Queue the response for GUI update
        self.message_queue.put(("response", response))
        
    def on_enter_key(self, event):
        """Handle Enter key press"""
        if not event.state & 0x1:  # If Shift is not pressed
            self.send_message()
            return "break"  # Prevent default newline
        
    def toggle_voice(self):
        """Toggle voice recognition"""
        self.is_listening = not self.is_listening
        
        if self.is_listening:
            self.voice_button.config(text="🔴 Stop Listening", bg="#ef4444")
            self.status_label.config(text="● Listening...")
            self.add_message("JARVIS", "Voice recognition activated. I'm listening...", "system")
            # Start voice recognition in background
            threading.Thread(target=self.voice_recognition_loop, daemon=True).start()
        else:
            self.voice_button.config(text="🎤 Start Listening", bg="#a855f7")
            self.status_label.config(text="● Ready")
            self.add_message("JARVIS", "Voice recognition deactivated.", "system")
            
    def voice_recognition_loop(self):
        """Voice recognition loop (placeholder)"""
        # Integrate your speech recognition logic here
        while self.is_listening:
            import time
            time.sleep(0.1)
            # Your speech recognition code here
            
    def clear_chat(self):
        """Clear chat display"""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the chat history?"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.conversation_history.clear()
            self.add_message("JARVIS", "Chat history cleared.", "system")
            
    def save_history(self):
        """Save conversation history to file"""
        if not self.conversation_history:
            messagebox.showinfo("Save History", "No conversation history to save.")
            return
            
        filename = f"jarvis_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
            messagebox.showinfo("Save History", f"History saved to {filename}")
            self.add_message("JARVIS", f"Conversation history saved to {filename}", "system")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save history: {str(e)}")
            
    def show_stats(self):
        """Show conversation statistics"""
        total_messages = len(self.conversation_history)
        user_messages = sum(1 for msg in self.conversation_history if msg['sender'] == 'You')
        jarvis_messages = sum(1 for msg in self.conversation_history if msg['sender'] == 'JARVIS')
        
        stats = f"""Conversation Statistics:
        
Total Messages: {total_messages}
Your Messages: {user_messages}
JARVIS Messages: {jarvis_messages}
"""
        messagebox.showinfo("Statistics", stats)
        
    def open_settings(self):
        """Open settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x500")
        settings_window.configure(bg="#0a1128")
        
        # Add settings options here
        label = tk.Label(
            settings_window,
            text="Settings",
            bg="#0a1128",
            fg="#00d9ff",
            font=("Arial", 16, "bold")
        )
        label.pack(pady=20)
        
        # Placeholder for settings
        info_label = tk.Label(
            settings_window,
            text="Settings panel - Add your configuration options here",
            bg="#0a1128",
            fg="#6b7280",
            font=("Arial", 10)
        )
        info_label.pack(pady=10)
        
    def process_queue(self):
        """Process messages from the queue"""
        try:
            while True:
                msg_type, data = self.message_queue.get_nowait()
                
                if msg_type == "response":
                    self.add_message("JARVIS", data, "jarvis")
                    self.status_label.config(text="● Ready")
                    self.is_processing = False
                    
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)


def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = JarvisGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()