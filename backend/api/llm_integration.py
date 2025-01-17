# backend/api/llm_integration.py
import base64
from io import BytesIO
import os
from anthropic import Anthropic, AnthropicError

from utils.config import config
from utils.prompts import (
    DELTA_SYSTEM_PROMPT,
    EDUCATIONAL_GUIDE_PROMPT,
)
from modules.educational import get_educational_content
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import PIL.Image
import httpx
import google.auth
import traceback
from dotenv import load_dotenv
import asyncio
from functools import partial
load_dotenv()


client = Anthropic(api_key=config["ANTHROPIC_API_KEY"])
PROJECT_ID = os.environ.get("PROJECT_ID")
LOCATION = os.environ.get("LOCATION")

async def generate_image(prompt: str) -> str:
    """Generates an image using Imagen 3 based on the given prompt."""
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/imagegeneration:predict"

    try:
        # Explicitly request the cloud-platform scope
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        # Create a new request object
        request = google.auth.transport.requests.Request()

        # Refresh the credentials synchronously
        credentials.refresh(request)

        # Use the access token from the credentials
        access_token = credentials.token

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        data = {
        "instances": [
            {
            "prompt": prompt,
            }
        ],
        "parameters": {
            "aspectRatio": "16:9",  
            "sampleCount": 1,
        },
        }



        async with httpx.AsyncClient(timeout=120.0) as client:  # Increased timeout
            response = await client.post(url, headers=headers, json=data)

            # Check for HTTP errors
            if response.status_code != 200:
                print(f"HTTP error occurred: {response.status_code}")
                print(f"Response content: {response.text}")
                return None

            response.raise_for_status()

            # Check for empty response body
            if not response.content:
                print("Error: Empty response body received from Vertex AI API.")
                return None

            response_data = response.json()

            # Check if the response contains the expected data
            if "predictions" in response_data and response_data["predictions"]:
                base64_image = response_data["predictions"][0].get("bytesBase64Encoded")
                if base64_image:
                    try:
                        # Decode the base64 image
                        image_bytes = base64.b64decode(base64_image)
                        pil_image = PIL.Image.open(BytesIO(image_bytes))

                        # Convert the image to a data URI
                        buffered = BytesIO()
                        pil_image.save(buffered, format="PNG")
                        image_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                        data_uri = f"data:image/png;base64,{image_str}"

                        return data_uri
                    except Exception as e:
                        print(f"Error processing image data: {e}")
                        traceback.print_exc()  # Print traceback for image processing errors
                        return None
                else:
                    print("Error: 'bytesBase64Encoded' key not found in the response.")
                    print(f"Response content: {response_data}")
                    return None
            else:
                print("Error: 'predictions' key not found in the response.")
                print(f"Response content: {response_data}")
                return None

    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
        print(f"Response content: {e.response.text}")
        return None

    except Exception as e:
        print(f"Error generating image: {e}")
        traceback.print_exc() # Print traceback for other exceptions
        return None
    
async def generate_response(user_input: str, role: str = "DELTA"):
    """Generates a response from the LLM based on the user input and role."""

    if role == "DELTA":
        system_prompt = DELTA_SYSTEM_PROMPT
        try:
            print(f"Sending request to LLM with role: {role}")
            print(f"User input: {user_input}")

            # Run the synchronous code in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(
                    client.messages.create,
                    model=config["LLM_MODEL"],
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_input},
                    ],
                )
            )
            
            print(f"LLM response: {response}")
            return response.content[0].text

        except AnthropicError as e:
            print(f"Error generating response from LLM: {e}")
            return "Sorry, I encountered an error while processing your request."

    elif role == "EDUCATIONAL_GUIDE":
        system_prompt = EDUCATIONAL_GUIDE_PROMPT
        # Function definitions for the LLM to use
        functions = [
            {
                "name": "get_educational_content",
                "description": "Provides educational content on a given hydrological topic.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The hydrological topic to explain (e.g., 'hydrological cycle', 'watershed').",
                        },
                    },
                    "required": ["topic"],
                },
            }
        ]

        try:
            print(f"Sending request to LLM with role: {role}")
            print(f"User input: {user_input}")

            response = client.messages.create(
                model=config["LLM_MODEL"],
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_input},
                ],
                tools=functions,
            )
            print(f"LLM response: {response}")

            # Handle tool calls
            if response.content and response.content[0].type == "tool_use":
                tool_call = response.content[0]
                if tool_call.name == "get_educational_content":
                    topic = tool_call.input.get("topic")
                    content = get_educational_content(topic)

                    # Construct the messages for the follow-up request,
                    # combining the tool call and result into a single assistant message
                    messages = [
                        {"role": "user", "content": user_input},
                        {
                            "role": "assistant",
                            "content": [
                                {
                                    "type": "tool_use",
                                    "id": tool_call.id,
                                    "name": tool_call.name,
                                    "input": tool_call.input,
                                },
                                {
                                    "type": "text",
                                    "text": content,
                                }
                            ]
                        }
                    ]

                    final_response = client.messages.create(
                        model=config["LLM_MODEL"],
                        max_tokens=1024,
                        system=system_prompt,
                        messages=messages,
                    )
                    return final_response.content[0].text

            return response.content[0].text

        except AnthropicError as e:
            print(f"Error generating response from LLM: {e}")
            return "Sorry, I encountered an error while processing your request."
    
    else:
        raise ValueError(f"Unknown role: {role}")
    
async def generate_summary_from_messages(messages):
    """Generates a summary from a list of messages."""
    try:
        # Format messages for LLM prompt
        formatted_messages = "\n".join(
            f"{msg['sender']}: {msg['content']}" for msg in messages
        )

        # Construct the summarization prompt
        prompt = f"Please provide a concise summary of the following conversation:\n\n{formatted_messages}\n\nSummary:"

        print(f"Sending summarization request to LLM")
        print(f"Prompt: {prompt}")

        response = client.messages.create(
            model=config["LLM_MODEL"],
            max_tokens=512,  # Adjust as needed for summary length
            system=DELTA_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        print(f"LLM response: {response}")

        return response.content[0].text

    except AnthropicError as e:
        print(f"Error generating summary from LLM: {e}")
        return "Sorry, I encountered an error while generating the summary."