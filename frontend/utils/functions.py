import json
from datetime import datetime
from typing import Tuple
from zoneinfo import ZoneInfo
from utils.load_config import LoadConfig

APPCFG = LoadConfig()

# Simplified timezone data
TIMEZONE_DATA = {
    "tokyo": "Asia/Tokyo",
    "san francisco": "America/Los_Angeles",
    "paris": "Europe/Paris",
    "barcelona": "Europe/Madrid",
    "madrid": "Europe/Madrid",
    "pamplona": "Europe/Madrid",
}

# Define the function for the model
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current time in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name, e.g. San Francisco",
                    },
                },
                "required": ["location"],
            },
        }
    }
]


def get_current_time(location) -> str:
        """Get the current time for a given location"""
        print(f"get_current_time called with location: {location}")  
        location_lower = location.lower()
        
        for key, timezone in TIMEZONE_DATA.items():
            if key in location_lower:
                print(f"Timezone found for {key}")  
                current_time = datetime.now(ZoneInfo(timezone)).strftime("%I:%M %p")
                return json.dumps({
                    "location": location,
                    "current_time": current_time
                })
        
        print(f"No timezone data found for {location_lower}")  
        return json.dumps({"location": location, "current_time": "unknown"})


def run_conversation(user_query: str) -> Tuple[str, int]:
        # Initial user message
        system_prompt = APPCFG.agent_llm_system_role            # viene del repositorio de prompts
        user_prompt = user_query                                # viene del repositorio de prompts

        messages = [
             {"role": "system","content": f"{system_prompt}"}, 
             {"role": "user", "content": f"{user_prompt}"}
             ]

        # First API call: Ask the model to use the function
        response = APPCFG.azure_openai_client.chat.completions.create(
            model=APPCFG.deployment,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        # Process the model's response
        response_message = response.choices[0].message
        response_total_tokens = response.usage.total_tokens
        messages.append(response_message)

        print("Model's response:")
        print(response_message)
        print(f"Total tokens used: {response.usage.total_tokens}")

        # Handle function calls
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                if tool_call.function.name == "get_current_time":
                    function_args = json.loads(tool_call.function.arguments)
                    print(f"Function arguments: {function_args}")  
                    time_response = get_current_time(
                        location=function_args.get("location")
                    )
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": "get_current_time",
                        "content": time_response,
                    })
        else:
            print("No tool calls were made by the model.")  

        print("Messages: ")
        print(messages)
        
        # Second API call: Get the final response from the LLM
        final_response = APPCFG.azure_openai_client.chat.completions.create(
            model=APPCFG.deployment,
            messages=messages,
        )

        response_total_tokens += final_response.usage.total_tokens
        print(f"Total tokens used: {final_response.usage.total_tokens}")

        print()
        return final_response.choices[0].message.content, response_total_tokens
