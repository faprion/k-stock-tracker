import os
import time
import pandas as pd
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import yfinance as yf
from pykrx import stock
from google import genai

# ============================================================
# 1. 영업일 계산
# ============================================================
def prev_valid_day(date_str):
    d = datetime.strptime(date_str, "%Y%m%d") - timedelta(days=1)
    for _ in range(10):
        ds = d.strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_ticker(ds, market="KOSPI")
        if not df.empty:
            return ds
        d -= timedelta(days=1)
    raise RuntimeError("영업일을 찾지 못했습니다.")

today_str = prev_valid_day((datetime.today() + timedelta(days=1)).strftime("%Y%m%d"))
prev_str = prev_valid_day(today_str)
print(f"기준일: {today_str}, 전일: {prev_str}")

# ============================================================
# 2. 8종목 선정 (순매수 상위3 + 급증3 + 거래대금상위2)
# ============================================================
def get_foreign_net(date_str):
    kospi = stock.get_market_net_purchases_of_equities(date_str, date_str, "KOSPI", "외국인")
    kospi["시장"] = "KOSPI"
    kosdaq = stock.get_market_net_purchases_of_equities(date_str, date_str, "KOSDAQ", "외국인")
    kosdaq["시장"] = "KOSDAQ"
    return pd.concat([kospi, kosdaq])

foreign_today = get_foreign_net(today_str)
foreign_prev = get_foreign_net(prev_str)

top3_buy = foreign_today.sort_values("순매수거래대금", ascending=False).head(3)

merged = foreign_today[["종목명", "순매수거래대금", "시장"]].join(
    foreign_prev[["순매수거래대금"]], lsuffix="_오늘", rsuffix="_전일", how="left"
).fillna(0)
merged["증가폭"] = merged["순매수거래대금_오늘"] - merged["순매수거래대금_전일"]
merged_excl = merged.drop(index=top3_buy.index, errors="ignore")
top3_surge = merged_excl.sort_values("증가폭", ascending=False).head(3)

vol_kospi = stock.get_market_ohlcv_by_ticker(today_str, market="KOSPI")
vol_kospi["시장"] = "KOSPI"
vol_kosdaq = stock.get_market_ohlcv_by_ticker(today_str, market="KOSDAQ")
vol_kosdaq["시장"] = "KOSDAQ"
vol_today = pd.concat([vol_kospi, vol_kosdaq])
exclude_idx = list(top3_buy.index) + list(top3_surge.index)
vol_excl = vol_today.drop(index=exclude_idx, errors="ignore")
top2_volume = vol_excl.sort_values("거래대금", ascending=False).head(2)

selected = []
for idx, row in top3_buy.iterrows():
    selected.append((idx, row["종목명"], row["시장"], "Top Foreign Net Buy"))
for idx, row in top3_surge.iterrows():
    selected.append((idx, foreign_today.loc[idx, "종목명"], foreign_today.loc[idx, "시장"], "Sudden Surge"))
for idx, row in top2_volume.iterrows():
    selected.append((idx, stock.get_market_ticker_name(idx), row["시장"], "High Volume"))

print("선정된 8종목:", selected)

# ============================================================
# 3. 투자유의 지정내역 체크 (네이버금융, 텍스트 키워드 검색 — 검증 필요)
# ============================================================
def check_investment_caution(ticker):
    url = f"https://finance.naver.com/item/main.naver?code={ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = "euc-kr"
        soup = BeautifulSoup(res.text, "html.parser")
        page_text = soup.get_text()
        keywords = ["관리종목", "투자주의", "투자경고", "투자위험", "거래정지"]
        found = [kw for kw in keywords if kw in page_text]
        return ", ".join(found) if found else "없음"
    except Exception as e:
        return f"확인 실패({e})"

# ============================================================
# 4. yfinance로 종목별 상세 지표 수집
# ============================================================
usd_krw = yf.Ticker("KRW=X").history(period="1d")['Close'].iloc[-1]

def get_yfinance_detail(ticker, market):
    suffix = ".KS" if market == "KOSPI" else ".KQ"
    yf_ticker = yf.Ticker(f"{ticker}{suffix}")
    info = yf_ticker.info or {}
    hist = yf_ticker.history(period="2d")

    price = info.get("currentPrice") or (hist["Close"].iloc[-1] if not hist.empty else None)
    prev_close = info.get("previousClose") or (hist["Close"].iloc[-2] if len(hist) > 1 else None)
    change_pct = (price - prev_close) / prev_close * 100 if price and prev_close else None

    return {
        "가격": price,
        "등락률": change_pct,
        "시가총액": info.get("marketCap"),
        "52주최고": info.get("fiftyTwoWeekHigh"),
        "52주최저": info.get("fiftyTwoWeekLow"),
        "배당수익률": info.get("dividendYield"),
        "공식홈페이지": info.get("website"),
    }

def fmt_krw_usd(value):
    if value is None:
        return "정보 없음"
    try:
        return f"{value:,.0f} KRW (~${value/usd_krw:,.2f} USD)"
    except Exception:
        return "정보 없음"

# ============================================================
# 5. 8종목 데이터 통합
# ============================================================
market_data_text = f"Real-time Exchange Rate: 1 USD = {usd_krw:.2f} KRW\n\n"

for ticker, name, market, category in selected:
    detail = get_yfinance_detail(ticker, market)
    caution = check_investment_caution(ticker)
    time.sleep(1)

    market_data_text += f"""
[{category}] {name} ({ticker})
- 현재가: {fmt_krw_usd(detail['가격'])}
- 당일 등락률: {f"{detail['등락률']:+.2f}%" if detail['등락률'] is not None else '정보 없음'}
- 시가총액: {fmt_krw_usd(detail['시가총액'])}
- 52주 최고/최저: {fmt_krw_usd(detail['52주최고'])} / {fmt_krw_usd(detail['52주최저'])}
- 배당수익률: {f"{detail['배당수익률']*100:.2f}%" if detail['배당수익률'] else '정보 없음'}
- 투자유의 지정내역: {caution}
- 공식 홈페이지: {detail['공식홈페이지'] or '정보 없음'}
"""

print(market_data_text)

# ============================================================
# 6. Gemini 리포트 생성
# ============================================================
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

prompt = f"""
You are a professional financial blogger writing a daily market report on Korean stocks for foreign investors.
Use ONLY the ACCURATE REAL DATA provided below. DO NOT invent or change any numbers. If a field says "정보 없음" or "확인 실패", write "Data not available" instead of guessing.

=== REAL MARKET DATA (8 stocks) ===
{market_data_text}
=============================

For each of the 8 stocks, include:
- Ticker, Company Name, Category (Top Foreign Buy / Sudden Surge / High Volume)
- 1-3 Key Core Businesses (general knowledge is fine for this part only)
- All financial figures EXACTLY as given above
- Investment Caution Status (state exactly what was given)
- Brief market context (based on business/category, not invented numbers)
- Official Website (state exactly what was given; if unavailable, say "Not available")

End with this exact disclaimer:
"Disclaimer: The information provided in this post is for informational and educational purposes only and does not constitute financial or investment advice. Always conduct your own research before making investment decisions."
"""

interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input=prompt
)

with open("draft.txt", "w", encoding="utf-8") as f:
    f.write(interaction.output_text)

print("draft.txt generated successfully!")
