import os
import google.generativeai as genai

# Gemini API 키 설정
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 프롬프트 설정 (외국인 순매수 데이터 기반 쉬운 영문 초안 작성)
prompt = """
You are a financial content writer for global retail investors.
Write a blog post, an X (Twitter) thread, and a Substack newsletter draft based on today's Korean stock market foreign net buying data.

Requirements:
1. Language: Simple, everyday English (clear and easy for general readers).
2. Target: Foreign investors looking for Korean stock insights (focus on context behind data, local industry specifics).
3. Include a mandatory financial disclaimer at the end.
4. Output Format:
   - [Blog & Substack Draft] Title, Top Foreign Buys, Context/Why, Source, Disclaimer
   - [X Post] Short summary with key numbers and link placeholder.
"""

# AI 모델 호출 및 실행
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content(prompt)

# 생성된 초안 출력 및 저장
print(response.text)
with open("draft.txt", "w", encoding="utf-8") as f:
    f.write(response.text)
