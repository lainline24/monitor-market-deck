"""슬라이드용 데이터(data.js)와 matplotlib 차트(SVG)를 eda/ 결과에서 생성."""
import os
import json

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EDA = os.path.join(ROOT, "eda")
CHARTS = os.path.join(HERE, "assets", "charts")
os.makedirs(CHARTS, exist_ok=True)

BG, FG, MUTED, GRID, ACCENT = "#0B1220", "#E5E7EB", "#6B7280", "#1F2937", "#3B82F6"
plt.rcParams.update({
    "font.family": "Malgun Gothic", "axes.unicode_minus": False,
    "figure.facecolor": "none", "axes.facecolor": "none", "savefig.transparent": True,
    "text.color": FG, "axes.labelcolor": "#9CA3AF", "xtick.color": "#9CA3AF", "ytick.color": "#9CA3AF",
    "axes.edgecolor": GRID, "font.size": 15, "svg.fonttype": "path",
})


def csv(name):
    return pd.read_csv(os.path.join(EDA, name), encoding="utf-8-sig")


df = csv("00_상품_정제데이터.csv")
raw = json.load(open(os.path.join(ROOT, "raw_data.json"), encoding="utf-8"))
reviews = raw["reviews"]
man = lambda v: round(v / 10000)

# ---------- data.js : 슬라이드에 쓰는 모든 숫자 ----------
panel = csv("02_세부패널별_가격크기.csv")
family = csv("01_패널계열별_가격크기.csv")
band_panel = csv("10_패널x가격대_상품수.csv")
hz = csv("05_주사율구간별_가격크기.csv")
feat = csv("12_트렌드_기능탑재율.csv")
top = csv("13_트렌드_인기TOP10_vs_나머지.csv")
kw = csv("16_리뷰_키워드언급률.csv")
rstar = csv("18_리뷰_패널별_별점.csv")
corr = csv("15_수치변수_상관계수.csv").set_index("변수")
size = csv("04_크기별_가격.csv")

bands = ["20만원 미만", "20~30만원", "30~50만원", "50~100만원", "100만원 이상"]
bp = band_panel.set_index("패널계열")
data = {
    "overview": {"products": int(len(df)), "reviews": len(reviews), "brands": int(df["브랜드"].nunique()),
                 "malls": len({r["쇼핑몰"] for r in reviews})},
    "panels": [{"panel": r.패널, "family": "OLED" if "OLED" in r.패널 else ("VA" if r.패널 == "VA" else "IPS"),
                "n": int(r.상품수), "avg": int(r.평균가), "min": int(r.최저가), "max": int(r.최고가)}
               for r in panel.itertuples()],
    "family": [{"family": r.패널계열, "n": int(r.상품수), "share": float(r._11), "avg": int(r.평균가),
                "inch": float(r.평균인치), "hz": int(r.평균주사율)} for r in family.itertuples()],
    "bands": [{"band": b, "IPS": int(bp.loc["IPS", b]), "VA": int(bp.loc["VA", b]), "OLED": int(bp.loc["OLED", b])}
              for b in bands],
    "hz": [{"band": r.주사율구간, "n": int(r.상품수), "median": int(r.중앙가)} for r in hz.itertuples()],
    "features": [{"feature": r.기능, "rate": float(r._3), "with": int(r.탑재시_평균가), "without": int(r.미탑재시_평균가)}
                 for r in feat.itertuples()],
    "top": {r.순위그룹: {"n": int(r.상품수), "avg": int(r.평균가), "inch": float(r.평균인치),
                       "qhd": float(r.QHD비중), "oled": float(r.OLED비중), "malls": float(r.평균판매몰수)}
            for r in top.itertuples()},
    "keywords": [{"kw": r.키워드, "n": int(r.언급리뷰수), "rate": float(r._3)} for r in kw.itertuples()],
    "reviewStars": [{"family": r.패널계열, "n": int(r.리뷰수), "avg": float(r.평균별점), "perfect": float(r.만점비율)}
                    for r in rstar.itertuples()],
    "corr": {k: float(corr.loc["최저가", k]) for k in ["인치", "주사율Hz", "평점", "리뷰수", "판매몰수"]},
    "size": [{"size": r.크기구간, "n": int(r.상품수), "avg": int(r.평균가)} for r in size.itertuples()],
    "perfectReviews": sum(r["점수(100점)"] == 100 for r in reviews),
    "lowReviews": sum(r["점수(100점)"] < 80 for r in reviews),
    "over144": int((df["주사율Hz"] > 144).sum()),
    "year2026": int((df["등록연도"] == 2026).sum()),
}

# ---------- v2: 피드백 반영 분석 ----------
yv = df["최저가"] / 10000
oled = (df["패널계열"] == "OLED").astype(float)


def r2(cols):
    X = np.column_stack([np.ones(len(df))] + cols)
    beta = np.linalg.lstsq(X, yv, rcond=None)[0]
    e = yv - X @ beta
    return float(1 - (e ** 2).sum() / ((yv - yv.mean()) ** 2).sum()), beta


non = df[df["패널계열"] != "OLED"]
r2_both, beta_both = r2([df["인치"], oled])
data["v2"] = {
    "r2": {"size": round(r2([df["인치"]])[0], 2), "panel": round(r2([oled])[0], 2), "both": round(r2_both, 2)},
    "oledPremium": round(float(beta_both[2])),
    "sizeSlopeBoth": round(float(beta_both[1]), 1),
    "corrAll": round(float(df[["최저가", "인치"]].corr().iloc[0, 1]), 2),
    "corrNonOled": round(float(non[["최저가", "인치"]].corr().iloc[0, 1]), 2),
    "corrHzNonOled": round(float(non[["최저가", "주사율Hz"]].corr().iloc[0, 1]), 2),
    "slopeNonOled": round(float(np.polyfit(non["인치"], non["최저가"] / 10000, 1)[0]), 1),
    "nNonOled": int(len(non)), "nOled": int(oled.sum()),
}
cls = pd.read_csv(os.path.join(EDA, "23_불량키워드리뷰_수동분류.csv"), encoding="utf-8-sig")
order = ["불량 없음 확인", "무관(오탐)", "빛샘 단점 언급", "기타 부품 불량 경험", "패널 불량 경험"]
data["v2"]["defect"] = [{"label": k, "n": int((cls["분류"] == k).sum())} for k in order]
# 화면 정보량(해상도 화소수 x 주사율) 대비 가격 — 표본 2종 이상 구간
PX = {"FHD": 1920 * 1080, "QHD": 2560 * 1440, "4K UHD": 3840 * 2160, "Ultra WQHD": 3440 * 1440, "WUHD": 5120 * 2160}
v = df.assign(seg=df["인치"].astype(int).astype(str) + "인치 " + df["해상도등급"].str.replace(" UHD", "") + " " + df["패널계열"],
              wpx=df["최저가"] / (df["해상도등급"].map(PX) * df["주사율Hz"] / 1e9),
              whz=df["최저가"] / df["주사율Hz"])
g = v.groupby("seg").agg(n=("pcode", "count"), wpx=("wpx", "median"), whz=("whz", "median"), price=("최저가", "median"))
g.round(0).sort_values("wpx").reset_index().rename(columns={"wpx": "화면정보량당가격_중앙값", "whz": "Hz당가격_중앙값", "price": "중앙가"})     .to_csv(os.path.join(EDA, "24_가성비_구간별_화면정보량당가격.csv"), index=False, encoding="utf-8-sig")
base = g.loc["27인치 QHD IPS", "wpx"]
data["v2"]["valueSingle"] = [{"seg": k, "n": int(r.n), "index": round(float(r.wpx / base), 2)}
                             for k, r in g[g["n"] == 1].sort_values("wpx").iterrows()]
g = g[g["n"] >= 2].sort_values("wpx")
data["v2"]["value"] = [{"seg": k, "n": int(r.n), "index": round(float(r.wpx / base), 2), "wonPerHz": int(round(r.whz)),
                        "price": int(r.price)} for k, r in g.iterrows()]
with open(os.path.join(HERE, "data.js"), "w", encoding="utf-8") as f:
    f.write("window.DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")
with open(os.path.join(HERE, "data.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

# ---------- 차트 1: 크기 vs 가격 산점도 ----------
fig, ax = plt.subplots(figsize=(12, 6.4))
d = df.copy()
d["jit"] = d.groupby("인치").cumcount()
cnt = d.groupby("인치")["인치"].transform("count")
d["x"] = d["인치"] + (d["jit"] - (cnt - 1) / 2) * 0.12
for fam, color, z in [("IPS", "#94A3B8", 2), ("VA", "#CBD5E1", 2), ("OLED", ACCENT, 3)]:
    s = d[d["패널계열"] == fam]
    ax.scatter(s["x"], s["최저가"] / 10000, s=140 if fam == "OLED" else 90, color=color, alpha=0.9,
               edgecolor=BG, linewidth=1.2, zorder=z, label={"IPS": "IPS 계열", "VA": "VA", "OLED": "OLED 계열"}[fam])
nd = d[d["패널계열"] != "OLED"]
m, b = np.polyfit(nd["인치"], nd["최저가"] / 10000, 1)
xs = np.array([23.5, 40.8])
ax.plot(xs, m * xs + b, color="#F59E0B", lw=2.5, ls="--", alpha=0.9, zorder=1)
ax.text(36.6, 112, f"IPS·VA {len(nd)}종 추세선\n1인치당 +{m:.1f}만 원 (r = {data['v2']['corrNonOled']:.2f})",
        color="#F59E0B", ha="center", va="center", fontsize=15, linespacing=1.4)
od = d[d["패널계열"] == "OLED"]
ax.text(od["x"].min() - 0.4, 160, "OLED 5종은 같은 크기에서도\n추세선보다 훨씬 위", ha="right", va="center",
        fontsize=15, color="#60A5FA", linespacing=1.4)
ax.set_xlabel("화면 크기 (인치)")
ax.set_ylabel("최저가 (만 원)")
ax.set_xticks([24, 27, 32, 34, 39, 40])
ax.set_ylim(0, 210)
ax.grid(axis="y", color=GRID, lw=1)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
ax.legend(frameon=False, loc="upper left", fontsize=14)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "size_price.svg"))
plt.close(fig)

# ---------- 차트 2: 크기 x 해상도 히트맵 ----------
cnt = csv("08_크기x해상도_상품수.csv").set_index("크기구간")
avg = csv("09_크기x해상도_평균가.csv").set_index("크기구간")
cols = ["FHD", "QHD", "4K UHD", "Ultra WQHD", "WUHD"]
cnt, avg = cnt[cols], avg[cols]
fig, ax = plt.subplots(figsize=(12, 5.6))
from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list("b", ["#111827", "#1E3A8A", ACCENT])
ax.imshow(cnt.values, cmap=cmap, aspect="auto", vmin=0, vmax=cnt.values.max())
for i in range(cnt.shape[0]):
    for j in range(cnt.shape[1]):
        n = cnt.values[i, j]
        if n:
            ax.text(j, i - 0.12, f"{n}종", ha="center", va="center", fontsize=22, fontweight="bold", color="white")
            ax.text(j, i + 0.22, f"평균 {man(avg.values[i, j])}만 원", ha="center", va="center", fontsize=13, color="#CBD5E1")
        else:
            ax.text(j, i, "–", ha="center", va="center", color="#374151", fontsize=16)
ax.set_xticks(range(len(cols)), ["FHD", "QHD", "4K UHD", "울트라와이드\nQHD", "5K\n(WUHD)"])
ax.set_yticks(range(len(cnt.index)), cnt.index)
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
ax.set_xticks(np.arange(-.5, len(cols)), minor=True)
ax.set_yticks(np.arange(-.5, len(cnt.index)), minor=True)
ax.grid(which="minor", color=BG, lw=4)
ax.tick_params(which="minor", length=0)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "size_res_heatmap.svg"))
plt.close(fig)

# ---------- 차트 3: 기능 프리미엄 덤벨 ----------
f = feat.assign(ratio=feat["탑재시_평균가"] / feat["미탑재시_평균가"]).sort_values("ratio")
fig, ax = plt.subplots(figsize=(12, 6))
y = np.arange(len(f))
ax.hlines(y, f["미탑재시_평균가"] / 1e4, f["탑재시_평균가"] / 1e4, color="#374151", lw=6, zorder=1)
ax.scatter(f["미탑재시_평균가"] / 1e4, y, s=220, color="#94A3B8", zorder=2, label="미탑재 평균가")
ax.scatter(f["탑재시_평균가"] / 1e4, y, s=220, color=ACCENT, zorder=3, label="탑재 평균가")
for yi, r in zip(y, f.itertuples()):
    ax.text(108, yi, f"{r.ratio:.1f}배", va="center", ha="left", fontsize=18, fontweight="bold",
            color=ACCENT if r.ratio >= 2 else "#9CA3AF")
ax.set_yticks(y, [f"{r.기능}  ({r._3:.0f}%)".replace("4K이상", "4K 이상") for r in f.itertuples()])
ax.set_xlim(0, 120)
ax.set_xticks([0, 25, 50, 75, 100], ["0", "25만", "50만", "75만", "100만"])
ax.set_xlabel("평균 최저가   ·   괄호 안 = 탑재율")
ax.grid(axis="x", color=GRID)
for s in ["top", "right", "left"]:
    ax.spines[s].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.legend(frameon=False, loc="upper center", fontsize=14, ncol=2, bbox_to_anchor=(0.45, 1.12))
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "feature_premium.svg"))
plt.close(fig)

print("data.js + charts:", sorted(os.listdir(CHARTS)))
