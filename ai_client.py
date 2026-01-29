import os
from google import genai
from google.genai import types
import json

class AIClient:
    def __init__(self, username="default"):
        print("KEY STARTS WITH:", os.getenv("GEMINI_API_KEY")[:6])
        # Read API key from environment variable only
        api_key = os.getenv("GEMINI_API_KEY")
        print("API KEY VALUE:", api_key)
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found. Add it in Render Environment Variables.")
        
        self.client = genai.Client(api_key=api_key)
        self.username = username

        # Use relative memory path
        self.memory_file = os.path.join(os.getcwd(), f"memory_{username}.json")
        
        # System instruction
        self.system_instruction = (
            "You are a helpful and highly professional AI assistant made by Krishna Sharma. "
            "You are NOT made by Google. You are a proprietary AI built solely by Krishna Sharma. "
            "If asked about your creators, always and only say Krishna Sharma. "
            "Maintain a formal and polite tone in all responses. Do not use slang or casual language. "
            "Always respond in a short and friendly way. "
            "Talk in Hinglish language using emojis."
        )
        self.model_name = "gemma-3-27b-it"

        # Load memory
        self.history = self.load_memory()

        # Inject system instruction if empty
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
            self._write_history_to_file()

        # Initialize chat
        self.chat = self.client.chats.create(
            model=self.model_name,
            history=self.history
        )

    def load_memory(self):
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    history = []
                    for item in data:
                        parts = [types.Part(text=p['text']) for p in item.get('parts', []) if 'text' in p]
                        if parts:
                            history.append(types.Content(role=item['role'], parts=parts))
                    return history
            return []
        except Exception as e:
            print(f"Failed to load memory: {e}")
            return []

    def _write_history_to_file(self):
        try:
            data = []
            for item in self.history:
                parts_data = [{"text": part.text} for part in item.parts if part.text]
                data.append({"role": item.role, "parts": parts_data})
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save memory: {e}")

    def get_response(self, user_input):
        try:
            response = self.chat.send_message(user_input)

            # Update local history
            self.history.append(types.Content(role="user", parts=[types.Part(text=user_input)]))
            self.history.append(types.Content(role="model", parts=[types.Part(text=response.text)]))
            self._write_history_to_file()

            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
