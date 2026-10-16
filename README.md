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

## v3 변경 (2차 피드백 반영)
주사율 주장을 27인치 QHD IPS 12종 안에서 다시 검증해 "주사율도 올리지만 폭이 작다(100Hz당 약 5~6만 원)"로 고쳤습니다. 불량은 좁게(2.2%)·넓게(5.2%) 두 숫자를 함께 보여 주고, 가성비 지수는 두 가지 정의로 교차 확인했습니다. r·R²·추세선·중앙값은 처음 나오는 곳에 한 줄씩 설명을 달았습니다. 자세한 내용은 `PLAN_v3.md`에 있습니다.
