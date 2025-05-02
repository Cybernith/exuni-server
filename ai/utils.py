from ai.models import ChatMessage

import openai

from server.settings import OPENAI_API_KEY


class ChatGPTClient:
    def _init_(self, user=None, model="gpt-3.5-turbo"):
        self.api_key = OPENAI_API_KEY
        self.model = model
        self.user = user
        openai.api_key = self.api_key

    def get_chat_history(self):
        if not self.user:
            return []
        messages = ChatMessage.objects.filter(user=self.user).order_by("created_at")
        return [{"role": msg.role, "content": msg.content} for msg in messages]

    def ask(self, message: str, system_prompt: str = None):
        messages = self.get_chat_history()
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
        )

        if self.user:
            ChatMessage.objects.create(user=self.user, role="user", content=message)
            ChatMessage.objects.create(
                user=self.user,
                role="assistant",
                content=response["choices"][0]["message"]["content"]
            )

        return response["choices"][0]["message"]["content"]


MODEL_PRICING = {
    'gpt-3.5-turbo': 0.0015 / 1000,
    'gpt-4': 0.03 / 1000,
    'gpt-4-32k': 0.06 / 1000,
}


def calculate_cost(model_name: str, tokens_used: int) -> float:
    rate = MODEL_PRICING.get(model_name, 0)
    return round(rate *tokens_used)
