import os
from openai import OpenAI

api_key = os.getenv('GROK_API_KEY')
client = OpenAI(api_key=api_key
                , base_url="https://api.x.ai/v1")


def grok_chat(user_input, message):
    message.append({"role": "user"
                    })


response = client.chat.completions.create

msg = response.choices[0].message
message.append(msg)
return msg.content
if __name__ == '__main__':
    messages = []
    while True:
        user_input = input("\n 질문을 입력하세요:(종료:q)")
        if user_input == 'q':
            break
        res = grok_chat(user_input, messages)
        print(res)
