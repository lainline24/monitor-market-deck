"""검증 1단계: 슬라이드 숫자를 원본 데이터에서 독립적으로 다시 계산해 대조 + 제목 금지어·모순 검사."""
import os
import re
import json

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
df = pd.read_csv(os.path.join(ROOT, "eda", "00_상품_정제데이터.csv"), encoding="utf-8-sig")
rv = pd.DataFrame(json.load(open(os.path.join(ROOT, "raw_data.json"), encoding="utf-8"))["reviews"])
rv = rv.merge(df[["pcode", "패널계열"]].astype({"pcode": str}), on="pcode", how="left")
cls = pd.read_csv(os.path.join(ROOT, "eda", "23_불량키워드리뷰_수동분류.csv"), encoding="utf-8-sig")
html = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
body = html.split("<body>")[1].split("<script>")[0]
text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"</?(?:b|em|small|span|strong)(?=[\s>])[^>]*>", "", body)))
man = lambda v: round(v / 10000)

oled_m = df.패널계열 == "OLED"
ips, oled, non = df[df.패널계열 == "IPS"], df[oled_m], df[~oled_m]
y = df.최저가 / 1e4


def r2(cols):
    X = np.column_stack([np.ones(len(df))] + cols)
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    return 1 - ((y - X @ b) ** 2).sum() / ((y - y.mean()) ** 2).sum(), b


r2s, r2p, (r2b, beta) = r2([df.인치])[0], r2([oled_m.astype(float)])[0], r2([df.인치, oled_m.astype(float)])
slope = np.polyfit(non.인치, non.최저가 / 1e4, 1)[0]
q27 = df[(df.인치 == 27) & (df.해상도등급 == "QHD")]
q32, k32 = df[(df.인치 == 32) & (df.해상도등급 == "QHD")], df[(df.인치 == 32) & (df.해상도등급 == "4K UHD")]
top = df[df.순위.notna() & (df.순위 <= 10)]
PX = {"FHD": 1920 * 1080, "QHD": 2560 * 1440, "4K UHD": 3840 * 2160, "Ultra WQHD": 3440 * 1440, "WUHD": 5120 * 2160}
seg = df.인치.astype(int).astype(str) + df.해상도등급 + df.패널계열
wpx = (df.최저가 / (df.해상도등급.map(PX) * df.주사율Hz)).groupby(seg).median()
whz = (df.최저가 / df.주사율Hz).groupby(seg).median()
idx = lambda k: wpx[k] / wpx["27QHDIPS"]
txt = rv.제목.fillna("") + " " + rv.내용.fillna("")
fhd = df[df.해상도등급 == "FHD"]
g27 = df[(df.인치 == 27) & (df.해상도등급 == "QHD") & (df.패널 == "Fast IPS") & (df.주사율Hz >= 200)]
c32 = df[(df.인치 == 32) & (df.해상도등급 == "4K UHD") & (df.패널 == "Fast IPS")]
o32 = df[(df.인치 == 32) & (df.패널 == "QD-OLED")]
feat = lambda col: df[df[col]].최저가.mean() / df[~df[col]].최저가.mean()
pnl_def = (cls.분류 == "패널 불량 경험").sum()

claims = [
    ("OLED 최저 vs IPS·VA 최고", f"OLED 88만 원이 IPS·VA 최고가 74만 원",
     f"OLED {man(oled.최저가.min())}만 원이 IPS·VA 최고가 {man(non.최저가.max())}만 원"),
    ("평균가 OLED vs IPS", "139만 vs 31만 원", f"{man(oled.최저가.mean())}만 vs {man(ips.최저가.mean())}만 원"),
    ("OLED 프리미엄(회귀)", "+94만 원", f"+{round(beta[2])}만 원"),
    ("50만 미만", "22 / 30종", f"{(df.최저가 < 500000).sum()} / {len(df)}종"),
    ("비OLED 크기 r", "r = 0.74", f"r = {non[['최저가', '인치']].corr().iloc[0, 1]:.2f}"),
    ("비OLED 기울기", "1인치당 약 3만 원", f"1인치당 약 {slope:.0f}만 원"),
    ("27→32 차이", "약 15만 원", f"약 {round(slope * 5)}만 원"),
    ("R² 패널 vs 크기", "0.75 vs 0.35", f"{r2p:.2f} vs {r2s:.2f}"),
    ("R² 둘 다", "0.84", f"{r2b:.2f}"),
    ("r 전체→비OLED", "0.59 → 0.74", f"{df[['최저가', '인치']].corr().iloc[0, 1]:.2f} → {non[['최저가', '인치']].corr().iloc[0, 1]:.2f}"),
    ("27QHD 수", "12 / 30종", f"{len(q27)} / {len(df)}종"),
    ("27QHD 평균", "평균 23만 원", f"평균 {man(q27.최저가.mean())}만 원"),
    ("32 QHD→4K", "3.2배", f"{k32.최저가.mean() / q32.최저가.mean():.1f}배"),
    ("32 4K 중 OLED", "7종 중 4종이 OLED", f"{len(k32)}종 중 {(k32.패널계열 == 'OLED').sum()}종이 OLED"),
    ("비OLED 주사율 r", "r = −0.08", f"r = {non[['최저가', '주사율Hz']].corr().iloc[0, 1]:.2f}".replace("-", "−")),
    ("260Hz 가격", "25~27만 원", f"{man(df[df.주사율Hz > 240].최저가.min())}~{man(df[df.주사율Hz > 240].최저가.max())}만 원"),
    ("144 이하 중앙가", "중앙가(18만 원)", f"중앙가({man(df[df.주사율Hz <= 144].최저가.median())}만 원)"),
    ("4K 배수", "4.1배", f"{feat('4K이상'):.1f}배"),
    ("피벗 배수", "1.1배", f"{feat('피벗'):.1f}배"),
    ("가성비 32 4K IPS", "1.31배", f"{idx('324K UHDIPS'):.2f}배"),
    ("가성비 FHD", "1.45배", f"{idx('27FHDIPS'):.2f}배"),
    ("가성비 OLED", "1.89배", f"{idx('324K UHDOLED'):.2f}배"),
    ("가성비 27 4K 단일", "0.86배", f"{idx('274K UHDIPS'):.2f}배"),
    ("Hz당 FHD vs QHD", "949원 vs 1,166원", f"{whz['27FHDIPS']:,.0f}원 vs {whz['27QHDIPS']:,.0f}원"),
    ("인기 1~10위 수", "광고 제외 6종", f"광고 제외 {len(top)}종"),
    ("인기 평균가", "평균 22만 원", f"평균 {man(top.최저가.mean())}만 원"),
    ("불량 키워드 건수", "리뷰 59건", f"리뷰 {len(cls)}건"),
    ("불량 없음 확인", "38건은", f"{(cls.분류 == '불량 없음 확인').sum()}건은"),
    ("패널 불량 경험", "6 / 269건 (2.2%)", f"{pnl_def} / {len(rv)}건 ({pnl_def / len(rv) * 100:.1f}%)"),
    ("키워드 매칭 일치", "59", str(txt.str.contains("불량|빛샘|데드픽셀|화소|멍").sum())),
    ("OLED 만점", "94%", f"{round((rv[rv.패널계열 == 'OLED']['점수(100점)'] == 100).mean() * 100)}%"),
    ("OLED 번인", "26%", f"{round(txt[rv.패널계열 == 'OLED'].str.contains('번인').mean() * 100)}%"),
    ("FHD 가격", "11~14만 원", f"{man(fhd.최저가.min())}~{man(fhd.최저가.max())}만 원"),
    ("게임 가격", "19~27만 원", f"{man(g27.최저가.min())}~{man(g27.최저가.max())}만 원"),
    ("32 4K Fast 가격", "50~74만 원", f"{man(c32.최저가.min())}~{man(c32.최저가.max())}만 원"),
    ("32 QD-OLED 가격", "88~175만 원", f"{man(o32.최저가.min())}~{man(o32.최저가.max())}만 원"),
]
fail = 0
for name, shown, computed in claims:
    ok = shown == computed and shown in text
    fail += not ok
    note = "" if shown in text else " (슬라이드에 문구 없음)"
    print(f"[{'OK ' if ok else 'FAIL'}] {name:<18} 슬라이드={shown:<22} 계산={computed}{note}")

# 제목 금지어 · 모순 검사
titles = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)).strip() for t in re.findall(r"<h[12][^>]*>(.*?)</h[12]>", body, re.S)]
banned = ["시장", "점유율", "장악", "TOP10", "정답", "불량률", "크기가 가격을 가장", "가장 크게 가릅니다"]
print("\n제목 이어 읽기:")
for i, t in enumerate(titles, 1):
    hits = [b for b in banned if b in t]
    fail += bool(hits)
    print(f"  {i:>2}. {t}" + (f"   ← 금지어: {hits}" if hits else ""))
print(f"\n수치 {len(claims)}개 + 제목 {len(titles)}개 검사, 실패 {fail}개")
