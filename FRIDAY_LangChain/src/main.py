# FRIDAY_v0.0.1\src\main.py

from src.agent import create_friday_agent
from src.tool_logger import ToolLooger

def main():
    friday = create_friday_agent()
    conversation = []

    print("Friday is online. Type 'exit' to quit")

    # Chat with the agent
    while True:
        try:
            user_input = input("\nUser: ").strip()

            if user_input.lower() in {"exist", "quit"}:
                print("Friday signing off")
                break

            if not user_input:
                continue

            conversation.append(
                {
                    "role": "user",
                    "content": user_input
                }
            )

            result = friday.invoke(
                {
                    "messages": conversation
                },
                config={
                    "callbacks": [ToolLooger()]
                }
            )

            # Preserve the complete conversation, including tool calls
            conversation = result["messages"]

            # The final message contains Friday's response
            print("\nFRIDAY:", conversation[-1].content)
        
        except KeyboardInterrupt:
            print("\nFRIDAY: Goodbye!")
            break
        except Exception as exc:
            print(f"\nFRIDAY encountered an error: {exc}")

if __name__ == "__main__":
    main()

