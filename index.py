import speech_recognition as sr
import pyttsx3
import tkinter as tk
from tkinter import messagebox
import json
import re
import os
from threading import Thread

class TodoListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice-Enabled To-Do List")
        self.root.geometry("400x500")
        
        # Initialize speech recognizer and text-to-speech engine
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        
        # Task list
        self.tasks = self.load_tasks()
        
        # GUI Components
        self.task_listbox = tk.Listbox(root, height=15, width=40)
        self.task_listbox.pack(pady=10)
        
        self.task_entry = tk.Entry(root, width=40)
        self.task_entry.pack(pady=5)
        
        self.add_button = tk.Button(root, text="Add Task (Manual)", command=self.add_task_manual)
        self.add_button.pack(pady=5)
        
        self.remove_button = tk.Button(root, text="Remove Selected Task", command=self.remove_task_manual)
        self.remove_button.pack(pady=5)
        
        self.clear_button = tk.Button(root, text="Clear All Tasks", command=self.clear_tasks)
        self.clear_button.pack(pady=5)
        
        self.voice_button = tk.Button(root, text="Start Voice Input", command=self.start_voice_input)
        self.voice_button.pack(pady=5)
        
        # Populate listbox with existing tasks
        self.update_listbox()
        
        # Bind window close to save tasks
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_tasks(self):
        """Load tasks from tasks.json if it exists."""
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as f:
                return json.load(f)
        return []
    
    def save_tasks(self):
        """Save tasks to tasks.json."""
        with open("tasks.json", "w") as f:
            json.dump(self.tasks, f)
    
    def update_listbox(self):
        """Update the listbox with current tasks."""
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            self.task_listbox.insert(tk.END, task)
    
    def speak(self, text):
        """Speak the given text."""
        self.engine.say(text)
        self.engine.runAndWait()
    
    def add_task(self, task):
        """Add a task to the list."""
        if task and task not in self.tasks:
            self.tasks.append(task)
            self.update_listbox()
            self.save_tasks()
            self.speak(f"Task {task} added to the list.")
        elif task in self.tasks:
            self.speak("This task is already in the list.")
    
    def remove_task(self, task):
        """Remove a task from the list."""
        if task in self.tasks:
            self.tasks.remove(task)
            self.update_listbox()
            self.save_tasks()
            self.speak(f"Task {task} removed from the list.")
        else:
            self.speak("Task not found in the list.")
    
    def clear_tasks(self):
        """Clear all tasks."""
        self.tasks.clear()
        self.update_listbox()
        self.save_tasks()
        self.speak("All tasks cleared.")
    
    def add_task_manual(self):
        """Add task from entry box."""
        task = self.task_entry.get().strip()
        if task:
            self.add_task(task)
            self.task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Please enter a task.")
    
    def remove_task_manual(self):
        """Remove selected task from listbox."""
        try:
            selected = self.task_listbox.get(self.task_listbox.curselection())
            self.remove_task(selected)
        except:
            messagebox.showwarning("Selection Error", "Please select a task to remove.")
    
    def parse_command(self, command):
        """Parse voice command and execute action."""
        command = command.lower().strip()
        
        # Add task
        add_match = re.match(r"(add|put|insert)\s+(.+?)(?:\s+to\s+(?:my\s+)?list)?$", command)
        if add_match:
            task = add_match.group(2).strip()
            self.add_task(task)
            return
        
        # Remove task
        remove_match = re.match(r"(remove|delete)\s+(.+?)(?:\s+from\s+(?:my\s+)?list)?$", command)
        if remove_match:
            task = remove_match.group(2).strip()
            self.remove_task(task)
            return
        
        # List tasks
        if re.match(r"(list|show)\s+(?:all\s+)?tasks", command):
            if self.tasks:
                task_list = ", ".join(self.tasks)
                self.speak(f"Your tasks are: {task_list}")
            else:
                self.speak("Your to-do list is empty.")
            return
        
        # Clear tasks
        if re.match(r"clear\s+(?:all\s+)?tasks", command):
            self.clear_tasks()
            return
        
        self.speak("Sorry, I didn't understand the command. Try saying 'add task', 'remove task', 'list tasks', or 'clear tasks'.")
    
    def listen(self):
        print("DEBUG: Starting to listen for voice command...")
        try:
            with sr.Microphone() as source:
                 print("Microphone OPENED and READY for input")
                 self.speak("Listening for your command.")
                 self.recognizer.adjust_for_ambient_noise(source, duration=1)
                 print("READY : Adjusted for ambient noise")
            # Increase timeout and phrase_time_limit
                 audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                 print(f"DEBUG: Audio captured successfully (length: {len(audio.get_wav_data()) / 16000:.2f} seconds)")
            try:
                 # Try recognizing with alternatives for better debugging
                command = self.recognizer.recognize_google(audio, show_all=True)
                if isinstance(command, dict) and command.get('alternative'):
                    top_result = command['alternative'][0]['transcript']
                    confidence = command['alternative'][0].get('confidence', 'N/A')
                    print(f"DEBUG: Google recognized (top result): '{top_result}' (confidence: {confidence})")
                    print(f"DEBUG: All alternatives: {[alt['transcript'] for alt in command['alternative']]}")
                    self.speak(f"You said: {top_result}")
                    self.parse_command(top_result)
                else:
                    print("DEBUG: No recognition results returned")
                    self.speak("Could not understand the audio. Please try again.")
            except sr.UnknownValueError:
                print("DEBUG: UnknownValueError - Google could not understand the audio")
                self.speak("Could not understand the audio. Please try again.")
            except sr.RequestError as e:
                print(f"DEBUG: RequestError - Could not request results from Google: {e}")
                self.speak("Speech recognition service is unavailable. Please try manual input.")
        except Exception as e:
             print(f"DEBUG: General error in listen: {e}")
             self.speak("An error occurred while listening. Please try again.")
       

    
    def start_voice_input(self):
        # """Start voice input in a separate thread to avoid freezing GUI."""
        print("DEBUG: Starting voice input thread")
        thread = Thread(target=self.listen, daemon=True)
        thread.start()
        print("DEBUG: Voice input thread started")
    
    def on_closing(self):
        """Save tasks and close the app."""
        self.save_tasks()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoListApp(root)
    root.mainloop()


# COMMANDS
# “Add paneer”
# “Remove paneer”
# “List tasks”