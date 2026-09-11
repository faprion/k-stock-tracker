import os
from google import genai

# Gemini API 클라이언트 설정 (보안을 위해 환경변수 사용)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

prompt = """
You are a professional financial blogger writing a daily market report on top Korean stocks for foreign investors.
Generate a concise, engaging daily update including key stock metrics, market context, and clear headers.

Categorize and cover these 8 stocks:
1. Semiconductor: Samsung Electronics (005930), SK Hynix (000660)
2. Battery/EV: LG Energy Solution (373220), POSCO Holdings (005490)
3. Automotive: Hyundai Motor (005380)
4. Defense/Aerospace: Hanwha Aerospace (012450)
5. Bio/Pharma: Samsung Biologics (207940)
6. Entertainment/Tech: NAVER (035420)

For each stock, present values in KRW ($USD equivalent) format using current market rates. Include market context, dividend details, primary business focus, and official website link.

At the very end of the post, always include this financial disclaimer:
"Disclaimer: The information provided in this post is for informational and educational purposes only and does not constitute financial or investment advice. Always conduct your own research before making investment decisions."
"""

# Gemini 최신 모델을 사용해 글 생성
response = client.models.generate_content(
    model='gemini-3.6-flash',
    contents=prompt,
)

# 결과를 draft.txt 파일로 저장
with open("draft.txt", "w", encoding="utf-8") as f:
    f.write(response.text)

print("draft.txt generated successfully!")
