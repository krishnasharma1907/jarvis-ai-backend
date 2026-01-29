import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class AIClient:
    def __init__(self, username="default"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
        
        self.client = genai.Client(api_key=api_key)
        self.username = username
        self.memory_file = f"c:/New folder/memory_{username}.json"
        
        # System instruction to define the persona
        self.system_instruction = "You are a helpful AI assistant made by Krishna Sharma. You are NOT made by Google. You are a proprietary AI built solely by Krishna Sharma. If asked about your creators, always and only say Krishna Sharma."
        self.model_name = "gemma-3-27b-it"

        # Load memory
        self.history = self.load_memory()

        # If memory is empty, inject system instruction
        if not self.history:
            self.history = [
                types.Content(
                    role="user",
                    parts=[types.Part(text=f"System Instruction: {self.system_instruction}")]
                ),
                types.Content(
                        role="model",
                        parts=[types.Part(text="Understood. I am a helpful AI assistant made by Krishna Sharma.")]
                )
            ]
            self.save_memory()

        # Initialize chat
        try:
            self.chat = self.client.chats.create(
                model=self.model_name,
                history=self.history
            )
        except Exception as e:
            raise ValueError(f"Failed to create chat with model '{self.model_name}'. Error: {e}")

    def load_memory(self):
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert JSON back to types.Content objects
                    history = []
                    for item in data:
                        parts = [types.Part(text=p['text']) for p in item.get('parts', []) if 'text' in p]
                        if parts:
                            history.append(types.Content(role=item['role'], parts=parts))
                    return history
            return []
        except Exception:
            return []

    def save_memory(self):
        try:
            # Convert types.Content to JSON-serializable format
            data = []
            # We can get history from the chat session or our self.history
            # The chat session history might be more up to date if we just sent a message
            # For this SDK, chat object maintains history. 
            # However, retrieving it might vary. Let's inspect self.chat.history if available, 
            # or just append manually if we want to be safe.
            # The google-genai SDK 0.x/1.x chat object usually exposes a history list.
            
            # Let's rely on extracting from the chat object if possible, 
            # otherwise we verify via the message we just sent.
            # Safe bet: The chat object likely has a history attribute. 
            # If not, we might need to verify the SDK structure.
            # Assuming self.chat._history or self.chat.history exists.
            # Google GenAI SDK `Chat` object usually has `_curated_history` or acts as a list wrapper?
            # Actually, let's just use the history variable we passed + new messages?
            # No, that's complex.
            # Let's assume standard `chat.history` property exists as a list of Content objects.
            pass # Placeholder logic handled in get_response to perform valid save
        except Exception:
            pass

    def get_response(self, user_input):
        try:
            response = self.chat.send_message(user_input)
            
            # Save to memory immediately
            # We need to access the updated history.
            # In the new SDK, chat history is automatically updated. 
            # We need to serialize the current state of chat history.
            
            # Serializing current history
            # Note: Accessing internal history might be SDK specific.
            # We will attempt to iterate over `self.chat._curated_history` or similar if `history` isn't public.
            # Standard public attribute is often just `history`.
            
            # For robustness, we will try to serialize self.chat.history
            # If that fails, we will manually append to our local self.history list and save that.
            
            current_history = []
            # 'chat' object in this SDK is likely 'google.genai.chats.Chat'
            # We need to check its attributes.
            # Given we can't inspect runtime, let's try assuming manual management is safer if unsure.
            # Manual management:
            # We initialized with self.history.
            # We just sent `user_input` and got `response.text`.
            # We should append these to self.history and save.
            
            self.history.append(types.Content(role="user", parts=[types.Part(text=user_input)]))
            self.history.append(types.Content(role="model", parts=[types.Part(text=response.text)]))
            
            self._write_history_to_file()
            
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
            
    def _write_history_to_file(self):
        try:
            data = []
            for item in self.history:
                # item is types.Content
                parts_data = []
                for part in item.parts:
                    if part.text:
                        parts_data.append({"text": part.text})
                data.append({
                    "role": item.role,
                    "parts": parts_data
                })
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save memory: {e}")
