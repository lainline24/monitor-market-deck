# 모니터 시장 분석 2026 — 슬라이드 덱

다나와 인기 모니터 30종과 쇼핑몰 리뷰 269건(2026-10-02 수집)을 분석한 HTML 슬라이드입니다.

- 조작: ← → 키, 스페이스, 스와이프, 하단 버튼 · URL `#번호`로 특정 슬라이드 열기
- 시각화: anime.js(인터랙티브 차트), matplotlib(정적 차트), manim(상관계수 애니메이션)
- 이미지: Google Flow(Nano Banana) 생성

## 다시 만들기
```bash
python build_assets.py                 # data.js + matplotlib 차트
python -m manim render -qh manim_corr.py CorrBars   # 영상 → assets/video/corr.mp4
python verify_numbers.py               # 수치 검증
python verify_render.py http://localhost:8765/ shots   # 렌더 검증
```
