import os
from openai import OpenAI

api_key = os.getenv('GROK_API_KEY')
client = OpenAI(api_key=api_key
                , base_url="https://api.x.ai/v1")


def grok_translate_en_to_ko(text, source_lang='english'
                            , target_lang='korean'):
    messages = [
        {"role": "system",
         "content": f"""you are a professional translator
                       translate all input from {source_lang}
                       to {target_lang}"""},
        {"role": "user",
         "content": text}
    ]
    response = client.chat.completions.create(
        model="grok-2-1212", messages=messages
    )
    return response.choices[0].message.content.strip()


if __name__ == '__main__':
    print(grok_translate_en_to_ko("hello, I am a developer."))
