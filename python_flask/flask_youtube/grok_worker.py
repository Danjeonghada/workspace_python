import os
from openai import OpenAI

api_key = os.getenv('GROK_API_KEY')
client = OpenAI(api_key=api_key
                , base_url="https://api.x.ai/v1")


system_instruction ="""
    너는 음식점 AI 비서야
    아래는 제공 가능한 메뉴와 가격이야. 아래 목록 외의 메뉴는
    절대 안내 하지마!
    
    메뉴 목록:
    - 삼겹살:13,000원
    - 물냉:9,000원
    - 공기밥:1,000원
    주의사항:
    - 위 메뉴 외에는 절대 제공하지 않음.
    - 메뉴를 물어 보면 가격까지 정확하게
    - 가격은 원 단위로 표시
    - 수량은 받을 수 있음.
"""


def ask(text):
    messages = [
        {"role": "system",
         "content": system_instruction},
        {"role": "user",
         "content": text}
    ]
    response = client.chat.completions.create(
        model="grok-2-1212", messages=messages
    )
    bot_text = response.choices[0].message.content
    messages.append({"role":"assistant", "content":bot_text})
    return bot_text
if __name__ == '__main__':
    while True:
        user_input=input("주문 하세요:")
        res = ask(user_input)
        print(f"bot:{res}")