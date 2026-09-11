import os
from google import genai

# Gemini API 키 설정 및 클라이언트 생성
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 프롬프트 설정 (8개 종목 구성, 단일 통화 표기 형식 KRW ($USD) 적용)
prompt = """
You are a financial content writer for global retail investors.
Write a blog post, an X (Twitter) thread, and a Substack newsletter draft based on Korean stock market foreign net buying and volume surge data.

Structure:
- Title Header: Include today's USD/KRW exchange rate right below the main title (e.g., USD/KRW: 1,340.74 KRW).
- Selected 8 Stocks:
  1. Top 3 Foreign Net Buys (Major leaders)
  2. Top 3 Surge Stocks (Rapid increase in foreign buying compared to yesterday)
  3. Top 2 High-Volume/Interest Stocks (High market attention regardless of foreign flow)

For EACH of the 8 stocks, provide the following structured details using a unified currency format `KRW ($USD)` (e.g., 298,000 KRW ($222.27 USD)):
- Ticker & Company Name
- Category & 1-3 Key Core Businesses
- Market Cap: Strictly format as `X Trillion KRW ($Y Billion USD)` (e.g., 52.10 Trillion KRW ($38.86 Billion USD))
- 52-Week High / Low: Strictly format as `High KRW ($High USD) / Low KRW ($Low USD)`
- Daily Price Change Rate (e.g., +10% or -5%)
- Last Dividend Amount & Dividend Yield: Strictly format as `Dividend KRW ($Dividend USD) / Yield%`
- Investment Caution / Warning Designation Status (for yesterday, today, and tomorrow if applicable; state "None" if clear)
- Why it is moving today (Market Context / Global Trends)
- Official Company Website Link at the bottom of each stock section

Requirements:
1. Language: Simple, everyday English for general readers. Avoid complex jargon.
2. Formats: Uniform currency display `KRW ($USD)` for ALL monetary figures across all metrics.
3. Include a mandatory financial disclaimer at the end.
4. Output Format:
   - [Blog & Substack Draft] Title with Exchange Rate, 8 Categorized Stocks with Detailed Metrics, Market Summary, Source, Disclaimer
   - [X Post] Short summary thread with key highlights and link placeholder.
"""

# 최신 Gemini 모델 호출
response = client.models.generate_content(
    model='gemini-3.6-flash',
    contents=prompt,
)

# 생성된 초안 출력 및 저장
print(response.text)
with open("draft.txt", "w", encoding="utf-8") as f:
    f.write(response.text)
