"""검증 2~3단계: 전 슬라이드 스크린샷 + 콘솔 에러·404·화면 밖 요소·잘린 텍스트 자동 점검.
usage: python verify_render.py <url> <out_dir> [--mobile]"""
import sys
import os
import json

from playwright.sync_api import sync_playwright

url, out = sys.argv[1], sys.argv[2]
mobile = "--mobile" in sys.argv
os.makedirs(out, exist_ok=True)

CHECK_JS = """
() => {
  const s = document.querySelector('.slide.active');
  const stage = document.getElementById('stage').getBoundingClientRect();
  const issues = [];
  const scale = stage.width / 1920;
  s.querySelectorAll('*').forEach(e => {
    const r = e.getBoundingClientRect();
    if (!r.width || !r.height) return;
    if (getComputedStyle(e).visibility === 'hidden') return;
    const tag = e.tagName.toLowerCase();
    if (['div','bg','shade'].includes(e.className)) return;
    if (e.classList.contains('bg')) return;
    const pad = 2;
    if (r.right > stage.right + pad || r.bottom > stage.bottom + pad || r.left < stage.left - pad || r.top < stage.top - pad)
      issues.push(`out-of-stage: <${tag} class="${e.getAttribute('class')||''}"> ${(e.textContent||'').trim().slice(0,40)}`);
    if (tag !== 'svg' && e.closest('svg') === null && e.scrollHeight > e.clientHeight + 4 && getComputedStyle(e).overflow !== 'visible')
      issues.push(`clipped: <${tag} class="${e.getAttribute('class')||''}"> ${(e.textContent||'').trim().slice(0,40)}`);
  });
  // 같은 부모 안 텍스트 노드 겹침 (svg text 포함)
  const texts = [...s.querySelectorAll('svg text')].map(t => ({t, r: t.getBoundingClientRect()})).filter(o => o.r.width);
  for (let i = 0; i < texts.length; i++) for (let j = i + 1; j < texts.length; j++) {
    const a = texts[i].r, b = texts[j].r;
    const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left), oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
    if (ox > 3 && oy > 3) issues.push(`svg-text-overlap: "${texts[i].t.textContent}" x "${texts[j].t.textContent}"`);
  }
  s.querySelectorAll('svg').forEach(sv => { const b = sv.getBoundingClientRect(); sv.querySelectorAll('text').forEach(t => { const r = t.getBoundingClientRect(); if (r.width && (r.right > b.right + 2 || r.left < b.left - 2 || r.top < b.top - 2 || r.bottom > b.bottom + 2)) issues.push('svg-text-clipped: ' + t.textContent); }); });
  s.querySelectorAll('img').forEach(i => { if (!i.complete || !i.naturalWidth) issues.push('broken-img: ' + i.src); });
  s.querySelectorAll('video').forEach(v => { if (v.readyState < 2) issues.push('video-not-ready: ' + v.currentSrc); });
  return {title: (s.querySelector('h1,h2')||{}).textContent, issues};
}
"""

report = {"console": [], "failed": [], "slides": []}
with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge")
    vp = {"width": 390, "height": 844} if mobile else {"width": 1920, "height": 1080}
    page = browser.new_page(viewport=vp, device_scale_factor=1)
    page.on("console", lambda m: report["console"].append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
    page.on("pageerror", lambda e: report["console"].append(f"pageerror: {e}"))
    page.on("requestfailed", lambda r: report["failed"].append(f"{r.url} {r.failure}"))
    page.on("response", lambda r: report["failed"].append(f"{r.status} {r.url}") if r.status >= 400 else None)
    page.goto(url + "#1", wait_until="networkidle")
    n = page.evaluate("document.querySelectorAll('.slide').length")
    for i in range(n):
        if i:
            page.keyboard.press("ArrowRight")
        page.wait_for_timeout(3800 if not mobile else 2500)
        res = page.evaluate(CHECK_JS)
        res["slide"] = i + 1
        report["slides"].append(res)
        page.screenshot(path=os.path.join(out, f"{'m' if mobile else 'd'}{i + 1:02d}.png"))
    browser.close()

bad = 0
for s in report["slides"]:
    flag = "OK " if not s["issues"] else "ISSUE"
    bad += bool(s["issues"])
    print(f"[{flag}] {s['slide']:>2}. {(s['title'] or '').strip()[:50]}")
    for it in s["issues"][:8]:
        print("      -", it)
print("console:", report["console"] or "없음")
print("failed requests:", report["failed"] or "없음")
print(f"문제 슬라이드 {bad}개")
