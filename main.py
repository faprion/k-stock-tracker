import os
import yfinance as yf
from google import genai

# 1. 8개 대표 종목 실시간 주가 수집 (Yahoo Finance 티커)
tickers = {
    "Samsung Electronics": "005930.KS",
    "SK Hynix": "000660.KS",
    "LG Energy Solution": "373220.KS",
    "POSCO Holdings": "005490.KS",
    "Hyundai Motor": "005380.KS",
    "Hanwha Aerospace": "012450.KS",
    "Samsung Biologics": "207940.KS",
    "NAVER": "035420.KS"
}

# 원/달러 실시간 환율 및 종목별 현재가 가져오기
usd_krw = yf.Ticker("KRW=X").history(period="1d")['Close'].iloc[-1]

market_data_text = f"Real-time Exchange Rate: 1 USD = {usd_krw:.2f} KRW\n\n"
for name, ticker in tickers.items():
    stock_info = yf.Ticker(ticker).history(period="1d")
    if not stock_info.empty:
        price = stock_info['Close'].iloc[-1]
        price_usd = price / usd_krw
        market_data_text += f"- {name} ({ticker}): {price:,.0f} KRW (~${price_usd:.2f} USD)\n"

# 2. Gemini API 클라이언트 설정 (보안 환경변수 사용)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

prompt = f"""
You are a professional financial blogger writing a daily market report on top Korean stocks for foreign investors.
Use the following ACCURATE REAL-TIME MARKET DATA provided below for stock prices and exchange rates. DO NOT invent or change any prices or exchange rates.

=== REAL-TIME MARKET DATA ===
{market_data_text}
=============================

Generate a concise, engaging daily update including key stock metrics, market context, and clear headers based on the data above.

Categorize and cover these 8 stocks:
1. Semiconductor: Samsung Electronics (005930.KS), SK Hynix (000660.KS)
2. Battery/EV: LG Energy Solution (373220.KS), POSCO Holdings (005490.KS)
3. Automotive: Hyundai Motor (005380.KS)
4. Defense/Aerospace: Hanwha Aerospace (012450.KS)
5. Bio/Pharma: Samsung Biologics (207940.KS)
6. Entertainment/Tech: NAVER (035420.KS)

For each stock, report the EXACT stock price provided in KRW ($USD equivalent). Include market context, dividend details, primary business focus, and official website link.

At the very end of the post, always include this financial disclaimer:
"Disclaimer: The information provided in this post is for informational and educational purposes only and does not constitute financial or investment advice. Always conduct your own research before making investment decisions."
"""

# 3. 구글 GenAI 최신 모델 호출
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
)

# 4. 결과를 draft.txt 파일로 저장
with open("draft.txt", "w", encoding="utf-8") as f:
    f.write(response.text)

print("draft.txt generated successfully with real-time stock data!")
