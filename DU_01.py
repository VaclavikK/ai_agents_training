import json
from ollama import Client, chat, ChatResponse
from typing import List, Dict, Any


MODEL = "gemma4:26b"
OLLAMA_HOST = "http://localhost:11434"

client = Client(host=OLLAMA_HOST)

# Function Implementations
def calculate(a: float, b: float, operation: str):
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            return {"error": "Division by zero"}
        result = a / b
    else:
        return {"error": f"Unknown operation: {operation}"}
    return {
        "result": result
    }
    
    

# Define tools for Ollama
tools = [
    calculate,
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Use this function to perform mathematical calculations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "The first number"
                    },
                    "b": {
                        "type": "number",
                        "description": "The second number"
                    },
                    "operation": {
                        "type": "string",
                        "description": "The operation to perform: add, subtract, multiply, or divide"
                    }
                },
                "required": ["a", "b", "operation"]
            },
        },
    },
]


# Available functions for calling
available_functions = {
    "calculate": calculate
}

# Example usage
messages = [
    {"role": "user", "content": "What is 5 plus 5?"}
]


class ReactAgent:

    def __init__(
        self,
        model: str = MODEL,
        host: str = OLLAMA_HOST
    ):
        self.model = model
        self.client = Client(host=host)
        self.max_iterations = 10

    def _complete(
        self,
        messages: List[Dict[str, Any]]
    ) -> ChatResponse:

        return self.client.chat(
            model=self.model,
            messages=messages,
            tools=tools
        )

    def run(
        self,
        messages: List[Dict[str, Any]]
    ) -> str:

        """
        Run the ReAct loop until we get a final answer.
        """

        iteration = 0

        while iteration < self.max_iterations:

            iteration += 1

            print(f"\n--- Iteration {iteration} ---")

            # Call local Ollama model
            response = self._complete(messages)

            response_message = response.message

            print(f"LLM Response: {response_message}")

            # Add assistant response to conversation history
            messages.append(
                response_message.model_dump(exclude_none=True)
            )

            # Check if model requested tool calls
            if response_message.tool_calls:

                # Process ALL tool calls
                for tool_call in response_message.tool_calls:

                    function_name = tool_call.function.name

                    # Ollama returns arguments as a dictionary
                    function_args = tool_call.function.arguments

                    print(
                        f"Executing tool: "
                        f"{function_name}({function_args})"
                    )

                    # Find requested function
                    function_to_call = available_functions.get(
                        function_name
                    )

                    if function_to_call is None:

                        function_response = {
                            "error": f"Unknown function: {function_name}"
                        }

                    else:

                        try:
                            function_response = function_to_call(
                                **function_args
                            )

                        except (TypeError, ValueError) as e:

                            function_response = {
                                "error": str(e)
                            }

                    print(f"Tool result: {function_response}")

                    # Add tool result to conversation history
                    messages.append(
                        {
                            "role": "tool",
                            "tool_name": function_name,
                            "content": json.dumps(function_response)
                        }
                    )

                # Continue ReAct loop
                continue

            else:

                # No tool calls - final answer
                final_content = response_message.content or ""

                print(f"\nFinal answer: {final_content}")

                return final_content

        return (
            "Error: Maximum iterations reached "
            "without getting a final answer."
        )


# ==========================================
# Main
# ==========================================

def main():

    print(f"Using model: {MODEL}")
    print(f"Ollama host: {OLLAMA_HOST}")
    print("Type 'exit' to quit.\n")

    agent = ReactAgent()

    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant that performs mathematical calculations based on user input."                
            )
        }
    ]

    while True:

        # Get user input
        user_input = input("\nYou: ").strip()

        # Exit application
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Ignore empty input
        if not user_input:
            continue

        # Add user message to conversation
        messages.append({
            "role": "user",
            "content": user_input
        })

        # Run ReAct agent
        result = agent.run(messages)

        print(f"\nAssistant: {result}")


if __name__ == "__main__":
    main()