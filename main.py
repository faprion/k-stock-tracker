from datetime import datetime, timedelta
from pykrx import stock

def prev_valid_day(date_str):
    """주어진 날짜보다 이전의 가장 최근 영업일을 찾는다."""
    d = datetime.strptime(date_str, "%Y%m%d") - timedelta(days=1)
    for _ in range(10):
        ds = d.strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_ticker(ds, market="KOSPI")
        if not df.empty:
            return ds
        d -= timedelta(days=1)
    raise RuntimeError("영업일을 찾지 못했습니다.")

# 오늘(또는 가장 최근 영업일), 그 전 영업일 구하기
today_str = prev_valid_day((datetime.today() + timedelta(days=1)).strftime("%Y%m%d"))
prev_str = prev_valid_day(today_str)
print(f"기준일: {today_str}, 전일: {prev_str}")

# 1) 외국인 순매수 상위 3종목 (KOSPI + KOSDAQ 합산)
foreign_kospi = stock.get_market_net_purchases_of_equities(today_str, today_str, "KOSPI", "외국인")
foreign_kosdaq = stock.get_market_net_purchases_of_equities(today_str, today_str, "KOSDAQ", "외국인")
foreign_today = foreign_kospi._append(foreign_kosdaq) if hasattr(foreign_kospi, "_append") else foreign_kospi.append(foreign_kosdaq)
top3_buy = foreign_today.sort_values("순매수거래대금", ascending=False).head(3)
print("\n[순매수 상위 3]")
print(top3_buy[["종목명", "순매수거래대금"]])

# 2) 전일 대비 순매수 급증 3종목
foreign_prev_kospi = stock.get_market_net_purchases_of_equities(prev_str, prev_str, "KOSPI", "외국인")
foreign_prev_kosdaq = stock.get_market_net_purchases_of_equities(prev_str, prev_str, "KOSDAQ", "외국인")
foreign_prev = foreign_prev_kospi._append(foreign_prev_kosdaq) if hasattr(foreign_prev_kospi, "_append") else foreign_prev_kospi.append(foreign_prev_kosdaq)

merged = foreign_today[["종목명", "순매수거래대금"]].join(
    foreign_prev[["순매수거래대금"]], lsuffix="_오늘", rsuffix="_전일", how="left"
).fillna(0)
merged["증가폭"] = merged["순매수거래대금_오늘"] - merged["순매수거래대금_전일"]
merged_excl = merged.drop(index=top3_buy.index, errors="ignore")
top3_surge = merged_excl.sort_values("증가폭", ascending=False).head(3)
print("\n[전일 대비 순매수 급증 3]")
print(top3_surge[["종목명_오늘" if "종목명_오늘" in top3_surge.columns else "종목명", "증가폭"]])

# 3) 외국인과 무관하게 거래대금이 쏠린 상위 2종목
vol_kospi = stock.get_market_ohlcv_by_ticker(today_str, market="KOSPI")
vol_kosdaq = stock.get_market_ohlcv_by_ticker(today_str, market="KOSDAQ")
vol_today = vol_kospi._append(vol_kosdaq) if hasattr(vol_kospi, "_append") else vol_kospi.append(vol_kosdaq)
exclude_idx = list(top3_buy.index) + list(top3_surge.index)
vol_excl = vol_today.drop(index=exclude_idx, errors="ignore")
top2_volume = vol_excl.sort_values("거래대금", ascending=False).head(2)
print("\n[거래대금 상위 2 (외국인 무관)]")
print(top2_volume[["거래대금"]] if "거래대금" in top2_volume.columns else top2_volume.head())
