import os
from openai import OpenAI
import json
api_key = os.getenv('GROK_API_KEY')
client = OpenAI(api_key=api_key
                , base_url="https://api.x.ai/v1")
members = {
    "hong": {"name":"홍길동", "email":"hong@gmail.com"},
    "kim": {"name":"김팽수", "email":"kim@gmail.com"},
    "dong": {"name":"박동길", "email":"park@gmail.com"}
}
def get_member(name):
    for user_id, info in members.items():
        if info['name'] == name:
            return f"{name}의 이메일은 {info['email']}입니다."
        return f"{name}님의 정보는 찾을 수 없습니다."
    tools = [
        {
            "type":"function",
            "function":{
                "name":"get_member",
                "description":"화원 이름으로 이메일 정보를 조회",
                "parameters":{
                    "name":{
                        "type":"string",
                        "description":"회원 이름 (예: 김은대)"
                    }
                },
                "required":["name"]
            }
        }
    ]
    messages = [
        {"role":"system",
         "content":"""너는 친절한 고객 응대 챗봇이야.
                      아룸울 멀허묜 아매알울 첮어쥬눈 험슈룰 거작ㅎ 았오.
                      그 외에는 자유롭게 대화해."""
        }
        def ask(text):
        messages.append({"role":"user","content":text})
        response = client.chat.completions.create(
            model="grok-2-1212",
            messages=messages,
            tools=tools,

        )
