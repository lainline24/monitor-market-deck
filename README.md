# 모니터 가격, 무엇이 정할까? — 슬라이드 덱 (v2)

다나와 인기 모니터 30종과 쇼핑몰 리뷰 269건(2026-10-02 수집)을 분석한 HTML 슬라이드입니다.

- 조작: ← → 키, 스페이스, 스와이프, 하단 버튼 · URL `#번호`로 특정 슬라이드 열기
- 시각화: anime.js(인터랙티브 차트), matplotlib(정적 차트), manim(상관계수 애니메이션)
- 이미지: Google Flow(Nano Banana) 생성

## 다시 만들기
```bash
python build_assets.py                 # data.js + matplotlib 차트
python -m manim render -qh manim_r2.py R2Bars   # 반론 검증 영상 → assets/video/r2.mp4
python verify_numbers.py               # 수치 검증
python verify_render.py http://localhost:8765/ shots [--nofont]   # 렌더 검증 (웹폰트 차단 모드 포함)
```

## v2 변경 (발표 피드백 반영)
결론을 "패널이 먼저, 같은 패널 안에서는 크기"로 통일했고, 반론 검증 2장(OLED 착시 여부, 불량 언급 vs 경험)과 가성비 계산 1장을 추가했습니다. 자세한 내용은 `PLAN_v2.md`에 있습니다.
