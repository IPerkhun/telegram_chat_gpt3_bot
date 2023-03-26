import openai
from config import ConfigManager


class OpenAIManager:
    def __init__(self, openai_api_key=None):
        self.model_name = "gpt-3.5-turbo"
        if not openai_api_key:
            openai_api_key = ConfigManager().get_openai_api_key()
        self.openai_api_key = openai_api_key

    async def get_openai_response(self, messages):
        response = openai.ChatCompletion.create(
            api_key=self.openai_api_key,
            model=self.model_name,
            messages=messages,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.9,
        )
        text = response.choices[0]["message"]["content"]
        return text