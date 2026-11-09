# FRIDAY_LangGraph\src\main.py
from langchain_core.messages import HumanMessage
from src.graph import agent_graph

def main():
    print("Local Research agent is online")
    print("Type 'exit to quit. \n")

    conversation = []
    
    while True:
        user_input = input("You ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Agent: Goodbye")
            break
        
        if not user_input:
            continue

        conversation.append(
            HumanMessage(content=user_input)
        )
        print(f"conversation: {conversation}")

        try:
            print(f"trying")
            result = agent_graph.invoke(
                {
                    "messages": conversation,
                    "iteration": 0
                },
                config={
                    "recursion_limit": 20
                }
            )
            conversation = result["messages"]

            final_message = conversation[-1]

            print("\nAgent:")
            print(final_message.content)
            print()

        except Exception as error:
            print(f"\nAgent execution failed: {error}")
            traceback.print_exc()

if __name__ == "__main__":
    main()