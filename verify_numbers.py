"""검증 1단계: 슬라이드에 적힌 숫자를 원본 데이터에서 다시 계산해 대조."""
import os
import re
import json

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
df = pd.read_csv(os.path.join(ROOT, "eda", "00_상품_정제데이터.csv"), encoding="utf-8-sig")
rv = pd.DataFrame(json.load(open(os.path.join(ROOT, "raw_data.json"), encoding="utf-8"))["reviews"])
rv = rv.merge(df[["pcode", "패널계열", "브랜드"]].astype({"pcode": str}), on="pcode", how="left")
html = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
text = re.sub(r"<[^>]+>", " ", html)
man = lambda v: round(v / 10000)
pct = lambda a, b: round(a / b * 100)

ips, oled = df[df.패널계열 == "IPS"], df[df.패널계열 == "OLED"]
i27, i32 = df[df.인치 == 27], df[df.인치 == 32]
q27 = df[(df.인치 == 27) & (df.해상도등급 == "QHD")]
q32, k32 = df[(df.인치 == 32) & (df.해상도등급 == "QHD")], df[(df.인치 == 32) & (df.해상도등급 == "4K UHD")]
fast, plain = df[df.패널 == "Fast IPS"], df[df.패널 == "IPS"]
hz260 = df[df.주사율Hz > 240]
top = df[df.순위.notna() & (df.순위 <= 10)]
txt = rv.제목.fillna("") + " " + rv.내용.fillna("")
defect = txt.str.contains("불량|빛샘|데드픽셀|화소|멍").sum()
burn = txt[rv.패널계열 == "OLED"].str.contains("번인").mean()
low = rv[rv["점수(100점)"] < 80]
fhd = df[(df.해상도등급 == "FHD")]
g27 = df[(df.인치 == 27) & (df.해상도등급 == "QHD") & (df.패널 == "Fast IPS") & (df.주사율Hz >= 200)]
c32 = df[(df.인치 == 32) & (df.해상도등급 == "4K UHD") & (df.패널 == "Fast IPS")]
o32 = df[(df.인치 == 32) & (df.패널 == "QD-OLED")]
pivot_ratio = df[df.피벗].최저가.mean() / df[~df.피벗].최저가.mean()

claims = [
    ("IPS 점유율", f"{pct(len(ips), len(df))}%", "80%"),
    ("OLED 평균가", f"{man(oled.최저가.mean())}만 원", "139만 원"),
    ("IPS 평균가", f"{man(ips.최저가.mean())}만 원", "31만 원"),
    ("Fast vs IPS Hz", f"+{round(fast.주사율Hz.mean() - plain.주사율Hz.mean())}Hz", "+46Hz"),
    ("27인치 평균가", f"{man(i27.최저가.mean())}만 원", "22만 원"),
    ("32인치 평균가", f"{man(i32.최저가.mean())}만 원", "77만 원"),
    ("27인치 범위", f"{man(i27.최저가.min())}~{man(i27.최저가.max())}만 원", "11~36만 원"),
    ("32인치 범위", f"{man(i32.최저가.min())}~{man(i32.최저가.max())}만 원", "28~175만 원"),
    ("27QHD 점유", f"{pct(len(q27), len(df))}%", "40%"),
    ("27QHD 수", f"{len(q27)}종", "12종"),
    ("32 QHD→4K", f"{k32.최저가.mean() / q32.최저가.mean():.1f}배", "3.2배"),
    ("상관 크기", f"{df[['최저가', '인치']].corr().iloc[0, 1]:.2f}", "0.59"),
    ("상관 주사율", f"{df[['최저가', '주사율Hz']].corr().iloc[0, 1]:.2f}", "0.28"),
    ("상관 평점", f"{df[['최저가', '평점']].corr().iloc[0, 1]:.2f}", "0.15"),
    ("50만 미만 비중", f"{pct((df.최저가 < 500000).sum(), len(df))}%", "73%"),
    ("50만 미만 수", f"{(df.최저가 < 500000).sum()}종", "22종"),
    ("최저 OLED", f"{man(oled.최저가.min())}만 원", "88만 원"),
    ("144Hz 초과", f"{pct((df.주사율Hz > 144).sum(), len(df))}%", "70%"),
    ("260Hz 가격", f"{man(hz260.최저가.min())}~{man(hz260.최저가.max())}만 원", "25~27만 원"),
    ("144 이하 중앙가", f"{man(df[df.주사율Hz <= 144].최저가.median())}만 원", "18만 원"),
    ("피벗 배수", f"{pivot_ratio:.1f}배", "1.1배"),
    ("2026 신제품", f"{pct((df.등록연도 == 2026).sum(), len(df))}%", "50%"),
    ("TOP10 평균가", f"{man(top.최저가.mean())}만 원", "22만 원"),
    ("TOP10 판매몰", f"{round(top.판매몰수.mean())}곳", "82곳"),
    ("불량 언급", f"{pct(defect, len(rv))}%", "22%"),
    ("저평점 수", f"{len(low)}건", "8건"),
    ("저평점 최다 브랜드 건수", f"{low.브랜드.value_counts().iloc[0]}건", "7건"),
    ("OLED 만점", f"{pct((rv[rv.패널계열 == 'OLED']['점수(100점)'] == 100).sum(), (rv.패널계열 == 'OLED').sum())}%", "94%"),
    ("OLED 번인", f"{round(burn * 100)}%", "26%"),
    ("FHD 사무 가격", f"{man(fhd.최저가.min())}~{man(fhd.최저가.max())}만 원", "11~14만 원"),
    ("게임 가성비 가격", f"{man(g27.최저가.min())}~{man(g27.최저가.max())}만 원", "19~27만 원"),
    ("32 4K Fast 가격", f"{man(c32.최저가.min())}~{man(c32.최저가.max())}만 원", "50~74만 원"),
    ("32 QD-OLED 가격", f"{man(o32.최저가.min())}~{man(o32.최저가.max())}만 원", "88~175만 원"),
]
fail = 0
for name, computed, shown in claims:
    ok_val = computed == shown
    ok_html = shown in text
    flag = "OK " if ok_val and ok_html else "FAIL"
    fail += flag == "FAIL"
    print(f"[{flag}] {name:<18} 계산={computed:<14} 슬라이드={shown:<14} {'(슬라이드에 없음)' if not ok_html else ''}")
print(f"\n{len(claims)}개 중 실패 {fail}개")
