import json
from ollama import chat, ChatResponse

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

response: ChatResponse = chat(
    "gemma4:26b",
    messages=messages,
    tools=tools,
)

print("First response:", response.message)

if response.message.tool_calls:

    # Find the tool call content
    tool_call = response.message.tool_calls[0]

    # Extract tool name and arguments
    function_name = tool_call.function.name
    function_args = tool_call.function.arguments

    # Call the function
    function_to_call = available_functions[function_name]
    function_response = function_to_call(**function_args)

    print("Function response:", function_response)

    # Add function response to messages for the model to use
    messages.append(response.message)
    messages.append({
        "role": "tool", 
        "name": function_name,
        "content": json.dumps(function_response), 
    })

    # Get final response from model
    final_response = chat("gemma4:26b", messages=messages)
    print("Second response:", final_response.message.content)
else:
    print("No tool calls returned from model")