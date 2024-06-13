import requests
import json
import uuid
import time


class CozeChatCompletion:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Host": "api.coze.com",
            "Connection": "keep-alive"
        }

    def create(self, model, messages):

        query = messages[-1]['content'] if messages else ''
        data = {

            "bot_id": model,
            "user": "29032201862555",
            "query": query,
            "stream": False
        }

        response = requests.post(self.url, headers=self.headers, data=json.dumps(data))
        if response.status_code == 200:
            response_data = response.json()
            return self._convert_to_openai_response(response_data)
        else:
            response.raise_for_status()

    def _convert_to_openai_response(self, coze_response):
        choices = []
        for message in coze_response.get('messages', []):
            choices.append({
                'index': len(choices),
                'message': {
                    'role': message['role'],
                    'content': message['content']
                },
                'finish_reason': 'stop'
            })

        openai_response = {
            'id': coze_response['conversation_id'],
            'object': 'chat.completion',
            'created': int(time.time()),
            'model': 'coze',
            'choices': choices,
            'usage': {
                'prompt_tokens': len(coze_response.get('query', '').split()),
                'completion_tokens': sum(len(choice['message']['content'].split()) for choice in choices),
                'total_tokens': len(coze_response.get('query', '').split()) + sum(
                    len(choice['message']['content'].split()) for choice in choices)
            }
        }

        return openai_response

# 使用示例：
# import coze
# coze_api = coze.CozeChatCompletion(api_key='your-api-key')
# response = coze_api.create(model='gpt-3.5-turbo', messages=[{"role": "user", "content": "hello"}])
# print(response)
