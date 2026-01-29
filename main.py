import sys
from ai_client import AIClient

def main():
    # Force UTF-8 encoding for Windows console (to handle emojis)
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        
    print("Initializing AI... (Made by Krishna Sharma)")
    try:
        ai = AIClient()
    except ValueError as e:
        print(e)
        return
    except Exception as e:
        print(f"Failed to initialize AI: {e}")
        return

    print("AI is ready! Type 'exit' or 'quit' to stop.")
    print("-" * 50)

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue

            response = ai.get_response(user_input)
            print(f"AI: {response}")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
