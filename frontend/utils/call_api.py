import os
import requests
import json
from utils.load_config import LoadConfig
from typing import List, Tuple

APPCFG = LoadConfig()

class CallApi:
    """
    A CallApi class to interact with the API.
    """

    @staticmethod
    def respond(chatbot: List, message: str) -> Tuple[str, List, int]:
        """
        A method to call the API.

        Args:
            message (str): The message to send to the API.

        Returns:
            str: The response from the API.
        """

        data = {"question": message}

        response = requests.post(APPCFG.api_url, json=data, headers={'Content-Type': 'application/json'})
        json_response = response.text

        # parse the JSON response
        response_dict = json.loads(json_response)
        result_message = response_dict['message']
        result_tokens = response_dict['total_tokens']

        # return result
        chatbot.append((message, result_message))
        return "", chatbot, result_tokens
    
    @staticmethod
    def chat(chatbot: List, message: str, conversation_id: int) -> Tuple[str, List, int, str]:
        """
        A method to call the chat API with GET request.

        Args:
            conversation_id (int): The conversation ID to send to the API.
            message (str): The message to send to the API.

        Returns:
            str: The response from the API.
        """

        if conversation_id is None:
            response = requests.get(APPCFG.api_url + f"?message={message}", headers={'Content-Type': 'application/json'})
        else:
            response = requests.get(APPCFG.api_url + f"?conversation_id={conversation_id}&message={message}", headers={'Content-Type': 'application/json'})
        
        json_response = response.text

        # parse the JSON response
        response_dict = json.loads(json_response)
        result_conversation_id = response_dict['conversation_id']
        result_message = response_dict['response']
        output_text = response_dict['output']
        
        # result_tokens = response_dict['total_tokens']
        result_tokens = 0

        # return result
        chatbot.append((message, result_message))
        return "", chatbot, result_conversation_id, output_text