# AI Agent Training 🤖

This repository contains source code and hands-on exercises from **AI Agent Training**.

All examples use a locally running **Ollama** instance and the **`gemma4:26b`** model. Communication happens directly through the `ollama` Python library, without LiteLLM or a cloud API.

The repository will be expanded with more exercises over time.

## Exercise Overview

| Exercise | Topic | Description |
| --- | --- | --- |
| 01 | **Interactive ReAct Agent** | Enter queries in the terminal, handle multiple tool calls in one response, run an iterative agent loop, and maintain conversation history. |

*More exercises will be added over time.*

## Exercise 01 – Interactive ReAct Agent with Ollama

This exercise extends basic tool calling with a `ReactAgent` class and interactive communication through the terminal.

For example, a user can enter:

```text
what is 44 * 55 and what is 5-4 and what is 9+9?
```

The agent sends the query to the local model, processes all requested calculations, and returns a combined answer. It then waits for another query. Type `exit` or `quit` to close the program.

### Agent Features

- **Interactive chat** – enter questions directly in the terminal using `input()`.
- **Tool calling** – the model can use the Python function `calculate()`.
- **Multiple tool calls** – the model can request multiple calculations in a single iteration.
- **Agent loop** – whenever the model calls a tool, its result is added to the conversation, allowing the model to continue.
- **Conversation history** – user messages, model responses, and tool results remain in the `messages` list while the program is running.
- **Iteration limit** – the agent allows up to 10 model calls per user query.

### Mathematical Tool

The `calculate(a, b, operation)` function supports the following operations:

| Operation | `operation` Parameter | Example |
| --- | --- | --- |
| Addition | `add` | `calculate(9, 9, "add")` → `18` |
| Subtraction | `subtract` | `calculate(5, 4, "subtract")` → `1` |
| Multiplication | `multiply` | `calculate(44, 55, "multiply")` → `2420` |
| Division | `divide` | `calculate(10, 2, "divide")` → `5.0` |

The function returns the result as `{"result": ...}`. Division by zero returns `{"error": "Division by zero"}`.

## Requirements and Setup

**Requirements:**

- Python 3.10+
- Ollama installed and running
- The `gemma4:26b` model available in Ollama
- The `ollama` Python library

**1. Install the Python library:**

```bash
pip install -U ollama
```

**2. Download the model:**

```bash
ollama pull gemma4:26b
```

**3. Make sure Ollama is running:**

```bash
ollama list
```

If Ollama is not running, you can start it with `ollama serve` (on some systems it starts automatically in the background).

**4. Save the agent code as `main.py` and run it:**

```bash
python main.py
```

The script connects to Ollama at `http://localhost:11434`. You can change the model and host by editing the `MODEL` and `OLLAMA_HOST` constants at the beginning of the file.

## Example Run

The following output is based on an actual run. Detailed `LLM Response` logs have been omitted for readability (the script itself prints them).

```text
Using model: gemma4:26b
Ollama host: http://localhost:11434
Type 'exit' to quit.

You: what is 44 * 55 and what is 5-4 and what is 9+9?

--- Iteration 1 ---
Executing tool: calculate({'a': 44, 'b': 55, 'operation': 'multiply'})
Tool result: {'result': 2420}
Executing tool: calculate({'a': 5, 'b': 4, 'operation': 'subtract'})
Tool result: {'result': 1}
Executing tool: calculate({'a': 9, 'b': 9, 'operation': 'add'})
Tool result: {'result': 18}

--- Iteration 2 ---
Final answer: 44 * 55 is 2,420, 5 - 4 is 1, and 9 + 9 is 18.

Assistant: 44 * 55 is 2,420, 5 - 4 is 1, and 9 + 9 is 18.

You: exit
Goodbye!
```

In the first iteration, the model requested three calls to the `calculate` tool at once. Python executed all three and added their results to the message history. In the second iteration, the model no longer needed any tools and generated the final answer.

The number of iterations and the exact wording of the answer may vary depending on the model's behavior and the user's query.

## How the Agent Loop Works

```text
User enters a query
        │
        ▼
Ollama: gemma4:26b
        │
        ├── Model requests tool call(s)
        │          │
        │          ▼
        │    Python executes calculate()
        │          │
        │          ▼
        │    Results are added to messages
        │          │
        │          └──────────► back to Ollama
        │
        └── Model does not request a tool
                   │
                   ▼
               Final answer
                   │
                   ▼
              Next user input
```

The following methods implement this workflow:

- **`ReactAgent._complete()`** – sends messages to the model using `self.client.chat(...)`.
- **`ReactAgent.run()`** – processes model responses, tool calls, and tool results in a loop.
- **`main()`** – waits for user input and maintains conversation history across queries.
