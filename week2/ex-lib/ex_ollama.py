# pip install ollama
# pip install --upgrade httpx
import ollama
models = ollama.list()
model_nm = 'mistral'
ollama.pull(model_nm)

# 대화 기록 (컨텍스트 유지)
messages = []
# messages.append({"role":"System"
#                  ,"content":"너는 친절한 AI 비서, 짧고 간결한 한글 답변을 제공해줘."})
print("exit or 종료 입력 시 종료")
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "종료"]:
        print("ollama 종료")
        break
    messages.append({"role":"user", "content": user_input})
    print("ollama AI:", end="", flush = True)
    # 스트리밍 응답 받기
    res_stream = ollama.chat(model=model_nm, messages=messages, stream=True)

    ai_all_response = ""
    for part in res_stream:
        text = part["message"]["content"]
        print(text, end="", flush=True)
        ai_all_response += text
    print()
    messages.append({"role": "assistant", "content": ai_all_response})
