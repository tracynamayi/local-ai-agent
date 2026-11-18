# Local AI Agent

A 100% free, locally hosted AI agent built with Python, Ollama, and LangGraph.
No API keys, no cloud services: everything runs on your own machine.

## Features

- Local LLM via Ollama (default: `llama3.2`)
- ReAct-style agent loop built with LangGraph's `create_react_agent`
- Short-term conversation memory using `MemorySaver`
- Local tools: file read/write (sandboxed), system info, calculator, date/time

## Project Structure

```
local-agent/
├── agent.py          # Builds the agent (model + tools + memory)
├── tools.py          # Tool definitions using @tool
├── main.py           # Terminal chat loop
└── requirements.txt
```

## Setup

1. Install [Ollama](https://ollama.com) and pull a model:
   ```
   ollama pull llama3.2
   ```
2. Create a virtual environment and install dependencies (Python 3.10+):
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Run the agent:
   ```
   python main.py
   ```

## Example

```
You: What is 25 * 4 + 10?
  [tool call] calculator({'expression': '25 * 4 + 10'})
  [tool result] 110
Agent: The answer to 25 * 4 + 10 is 110.
```

## Design Notes

- **Safe calculator:** math is parsed with Python's `ast` module, never `eval()`.
- **Sandboxed files:** file tools can only access the `workspace/` folder.
- **Memory:** conversation state is kept in RAM per `thread_id` and resets
  when the program exits.

## Known Limitations

- **Small models struggle with multi-step tool chains.** With `llama3.2` (3B),
  a prompt like *"calculate X, save it to a file, then read it back"* fails:
  the model either batches all tool calls at once (guessing values it hasn't
  received yet) or describes the next step in text instead of calling the tool.
  Stricter system-prompt rules changed the failure mode but did not fix it.
  Larger models such as `qwen2.5:7b` are expected to handle this better.
- Single-tool calls and memory work reliably.
- Memory is not persistent across runs.

## Tech Stack

Python 3.12 · Ollama · LangChain · LangGraph