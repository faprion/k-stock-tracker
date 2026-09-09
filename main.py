import os
from google import genai

# Gemini API 키 설정 및 클라이언트 생성
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 프롬프트 설정 (대중을 위한 쉬운 영어 작성 지침 포함)
prompt = """
You are a financial content writer for global retail investors.
Write a blog post, an X (Twitter) thread, and a Substack newsletter draft based on today's Korean stock market foreign net buying data.

Requirements:
1. Language: Simple, everyday English for general readers. Avoid jargon unless necessary.
2. Target: Foreign investors looking for Korean stock insights (focus on context behind data, local industry specifics).
3. Include a mandatory financial disclaimer at the end.
4. Output Format:
   - [Blog & Substack Draft] Title, Top Foreign Buys, Context/Why, Source, Disclaimer
   - [X Post] Short summary with key numbers and link placeholder.
"""

# 최신 Gemini 모델 호출
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
)

# 생성된 초안 출력 및 저장
print(response.text)
with open("draft.txt", "w", encoding="utf-8") as f:
    f.write(response.text)
