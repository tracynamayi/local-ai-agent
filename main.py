from langchain_core.messages import AIMessage, ToolMessage

from agent import build_agent

def main():
    agent = build_agent()

    config = {"configurable": {"thread_id":"session-1"}}

    print("Local agent ready. Type'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            break

        for update in agent.stream(
            {"messages": [("user", user_input)]},
            config,
            stream_mode="updates"
        ):
            for data in update.values():
                for msg in data.get("messages", []):
                    if isinstance(msg, AIMessage):
                        if msg.tool_calls:
                            for call in msg.tool_calls:
                                print(f"  [tool call] {call['name']}({call['args']})")
                        elif msg.content:
                            print(f"Agent: {msg.content}\n")
                    elif isinstance(msg, ToolMessage):
                        print(f"  [tool result] {msg.content}")


if __name__ == "__main__":
    main()