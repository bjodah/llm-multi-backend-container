#!/usr/bin/env python3
"""
This script originates from: https://github.com/ggml-org/llama.cpp/pull/14349#issue-3169415639

Tool calling test script for llama.cpp OpenAI-compatible endpoint
Tests the full flow: initial request -> tool call -> mock result -> final response
"""

import json
import requests
from typing import Dict, Any, List

# Configuration
API_URL = "http://localhost:8686/v1/chat/completions"
MODEL = "llamacpp-mistral-small-3.2-24b-2506"

# Tool definition
WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and country/state, e.g. `San Francisco, CA`, or `Paris, France`"
                }
            },
            "required": ["location"]
        }
    }
}

def make_request(messages: List[Dict[str, Any]], tools: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make a request to the API"""
    payload = {
        "model": MODEL,
        "messages": messages
    }

    if tools:
        payload["tools"] = tools

    response = requests.post(API_URL, json=payload, headers={"Authorization": "Bearer sk-empty"})
    response.raise_for_status()
    return response.json()

def get_mock_weather(location: str) -> Dict[str, Any]:
    """Generate mock weather data for a location"""
    # Mock weather data
    mock_data = {
        "Istanbul": {
            "temperature": 18,
            "condition": "partly cloudy",
            "humidity": 65,
            "wind_speed": 12
        },
        "default": {
            "temperature": 22,
            "condition": "sunny",
            "humidity": 50,
            "wind_speed": 8
        }
    }

    weather = mock_data.get(location.split(",")[0].strip(), mock_data["default"])

    return {
        "location": location,
        "temperature_celsius": weather["temperature"],
        "condition": weather["condition"],
        "humidity_percent": weather["humidity"],
        "wind_speed_kmh": weather["wind_speed"]
    }

def main():
    print("🚀 Testing tool calling with llama.cpp endpoint\n")

    # Initial conversation
    messages = [
        {"role": "system", "content": "You are a chatbot that uses tools/functions. Don't overthink things."},
        {"role": "user", "content": "What is the weather in Istanbul?"}
    ]

    print("📤 Sending initial request with tool definition...")
    print(f"User: {messages[-1]['content']}\n")

    # Step 1: Initial request with tool
    try:
        response = make_request(messages, [WEATHER_TOOL])
        print("📥 Received response:")
        print(json.dumps(response, indent=2))
        print()

        # Extract the assistant's response
        assistant_message = response["choices"][0]["message"]
        messages.append(assistant_message)

        # Check if the model made a tool call
        if "tool_calls" in assistant_message and assistant_message["tool_calls"]:
            tool_call = assistant_message["tool_calls"][0]
            function_name = tool_call["function"]["name"]
            function_args = json.loads(tool_call["function"]["arguments"])

            print(f"🔧 Model called tool: {function_name}")
            print(f"   Arguments: {function_args}\n")

            # Step 2: Execute the tool (mock)
            if function_name == "get_current_weather":
                location = function_args.get("location", "Unknown")
                weather_data = get_mock_weather(location)

                print(f"🌤️  Mock weather data for {location}:")
                print(json.dumps(weather_data, indent=2))
                print()

                # Step 3: Send tool result back to model
                tool_result_message = {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(weather_data)
                }
                messages.append(tool_result_message)

                print("📤 Sending tool result back to model...")
                final_response = make_request(messages)

                print("📥 Final response from model:")
                print(json.dumps(final_response, indent=2))
                print()

                # Extract and display the final answer
                final_content = final_response["choices"][0]["message"]["content"]
                print("💬 Assistant's final answer:")
                print(final_content)

                # Add the assistant's response to messages
                messages.append({
                    "role": "assistant",
                    "content": final_content
                })

                # Continue with more turns
                print("\n" + "="*60 + "\n")
                test_additional_turns(messages)
            else:
                print(f"❓ Unknown tool called: {function_name}")
        else:
            print("⚠️  Model did not make a tool call")
            if "content" in assistant_message:
                print(f"Model response: {assistant_message['content']}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
    except KeyError as e:
        print(f"❌ Unexpected response format, missing key: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_additional_turns(messages: List[Dict[str, Any]]):
    """Test additional conversation turns after tool usage"""
    print("🔄 Testing additional conversation turns...\n")

    # Turn 1: Follow-up question about the weather (no tool needed)
    print("📍 Turn 1: Follow-up question")
    messages.append({
        "role": "user",
        "content": "Is that good weather for sightseeing?"
    })
    print(f"User: {messages[-1]['content']}\n")

    try:
        response = make_request(messages)
        assistant_response = response["choices"][0]["message"]["content"]
        print(f"💬 Assistant: {assistant_response}\n")
        messages.append({
            "role": "assistant",
            "content": assistant_response
        })
    except Exception as e:
        print(f"❌ Error in turn 1: {e}\n")
        return

    print("-" * 40 + "\n")

    # Turn 2: Different topic (no tool needed)
    print("📍 Turn 2: Different topic")
    messages.append({
        "role": "user",
        "content": "By the way, what's the capital of Turkey?"
    })
    print(f"User: {messages[-1]['content']}\n")

    try:
        response = make_request(messages)
        assistant_response = response["choices"][0]["message"]["content"]
        print(f"💬 Assistant: {assistant_response}\n")
        messages.append({
            "role": "assistant",
            "content": assistant_response
        })
    except Exception as e:
        print(f"❌ Error in turn 2: {e}\n")
        return

    print("-" * 40 + "\n")

    # Turn 3: Another weather request (should trigger tool use again)
    print("📍 Turn 3: Another weather request with tool")
    messages.append({
        "role": "user",
        "content": "What about the weather in Paris, France?"
    })
    print(f"User: {messages[-1]['content']}\n")

    try:
        response = make_request(messages, [WEATHER_TOOL])
        assistant_message = response["choices"][0]["message"]

        if "tool_calls" in assistant_message and assistant_message["tool_calls"]:
            tool_call = assistant_message["tool_calls"][0]
            function_args = json.loads(tool_call["function"]["arguments"])

            print(f"🔧 Model called tool again: {tool_call['function']['name']}")
            print(f"   Arguments: {function_args}\n")

            # Get mock weather for Paris
            location = function_args.get("location", "Unknown")
            weather_data = get_mock_weather(location)

            print(f"🌤️  Mock weather data for {location}:")
            print(json.dumps(weather_data, indent=2))
            print()

            # Send tool result
            messages.append(assistant_message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": json.dumps(weather_data)
            })

            final_response = make_request(messages)
            final_content = final_response["choices"][0]["message"]["content"]
            print(f"💬 Assistant: {final_content}\n")
            messages.append({
                "role": "assistant",
                "content": final_content
            })
        else:
            print("⚠️  Model did not make a tool call for Paris weather")
            if "content" in assistant_message:
                print(f"Model response: {assistant_message['content']}")
    except Exception as e:
        print(f"❌ Error in turn 3: {e}\n")
        return

    print("-" * 40 + "\n")

    # Turn 4: Comparison question (no tool needed)
    print("📍 Turn 4: Comparison question")
    messages.append({
        "role": "user",
        "content": "Which city has better weather for visiting, Istanbul or Paris?"
    })
    print(f"User: {messages[-1]['content']}\n")

    try:
        response = make_request(messages)
        assistant_response = response["choices"][0]["message"]["content"]
        print(f"💬 Assistant: {assistant_response}\n")
    except Exception as e:
        print(f"❌ Error in turn 4: {e}\n")

    print("✅ Multi-turn conversation test complete!")

if __name__ == "__main__":
    main()
