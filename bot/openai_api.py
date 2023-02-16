import openai
import os

class OpenAIAPI:
    def __init__(self, openai_api_key):
        self.api_key = openai_api_key
        openai.api_key = openai_api_key

    def send_message(self, message, message_history=[]):     
        

        prompt = message
        

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=2048,
            n=1,
            stop=None,
            temperature=0.9,
            timeout=1200,
        )
        return response.choices[0].text
        