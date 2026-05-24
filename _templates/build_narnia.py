#!/usr/bin/env python3
"""
narnia 用クイズ HTML 組み立て。

wizard part1.html をスケルトンに、sections JSON + メタ + 冬テーマを差し替える。
fugashi+unidic-lite でふりがな辞書を自動生成。

Usage:
    .venv/bin/python build_narnia.py part1
    .venv/bin/python build_narnia.py part2
"""
import json, re, sys
from pathlib import Path

if len(sys.argv) < 2 or sys.argv[1] not in ('part1', 'part2'):
    print('Usage: build_narnia.py {part1|part2}', file=sys.stderr)
    sys.exit(1)

PART = sys.argv[1]
ROOT = Path('/home/tana/dev/yamaneko-quiz')
SKELETON = ROOT / '2-biome-wizard/part1.html'
NARNIA = ROOT / '3-narnia'

META = {
    'part1': {
        'sections_path': NARNIA / 'sections_part1.json',
        'output_path': NARNIA / 'part1.html',
        'app_title': 'ラップランドの冬 (前編) 国語クイズ',
        'title_h1': '❄️ ラップランドの冬 (前編)',
        'log_title': '❄️ ラップランドの冬 (前編)クイズ ログ',
        'save_key': 'narnia_part1_save',
        'log_key': 'narnia_part1_save_log',
    },
    'part2': {
        'sections_path': NARNIA / 'sections_part2.json',
        'output_path': NARNIA / 'part2.html',
        'app_title': 'ラップランドの冬 (後編) 国語クイズ',
        'title_h1': '❄️ ラップランドの冬 (後編)',
        'log_title': '❄️ ラップランドの冬 (後編)クイズ ログ',
        'save_key': 'narnia_part2_save',
        'log_key': 'narnia_part2_save_log',
    }
}

COMMON = {
    'mobile_title': 'ラップランド',
    'title_emoji': '❄️',
    'icon_bg_hex': '2d4561',
    'intro_html': '「ラップランドの冬」を読んで<br>クイズに答えよう！',
}

# 冬テーマ (オーロラ + 雪) で wizard 紫を上書き
SCENE_GRADIENT = 'linear-gradient(180deg, #0d1f3a 0%, #1e4068 18%, #3a7da8 35%, #6fadd0 50%, #b5dce9 58%, #e8f0f5 60%, #cad5dc 100%)'
SCENE_BORDER = '4px solid #8aa0b0'
GRASS_BG = 'linear-gradient(180deg, #e8f0f5 0%, #e8f0f5 35%, #b5c8d4 35%, #95acb8 100%)'
GRASS_BORDER = '1px solid #c5d4e0'
STAR_SHADOW = '0 0 6px #fff, 0 0 10px #4a6b8a'


def generate_furigana(sections):
    from fugashi import Tagger
    t = Tagger()
    buf = []
    for s in sections:
        buf.append(s['text'])
        for q in s['questions']:
            buf.append(q['q'])
            buf.extend(q['choices'])
            buf.append(q['explanation'])
    text = '\n'.join(buf)
    out = {}
    for w in t(text):
        surface = w.surface
        if not re.search(r'[一-龯々]', surface): continue
        if len(surface) > 8: continue
        kana = (w.feature.kana or '').strip()
        if not kana or kana == '*': continue
        hira = ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in kana)
        out[surface] = hira
    return out


def replace_block(html, start_marker, end_marker, replacement):
    start = html.find(start_marker)
    if start < 0: raise ValueError(f"start not found: {start_marker!r}")
    end_from = start + len(start_marker)
    end = html.find(end_marker, end_from)
    if end < 0: raise ValueError(f"end not found: {end_marker!r}")
    end += len(end_marker)
    return html[:start] + replacement + html[end:]


def main():
    meta = META[PART]
    html = SKELETON.read_text(encoding='utf-8')
    sections = json.loads(meta['sections_path'].read_text(encoding='utf-8'))
    furigana = generate_furigana(sections)

    # head
    html = re.sub(r'<title>.*?</title>', f"<title>{meta['app_title']}</title>", html, count=1)
    html = re.sub(
        r'<meta name="apple-mobile-web-app-title" content="[^"]*">',
        f"<meta name=\"apple-mobile-web-app-title\" content=\"{COMMON['mobile_title']}\">",
        html
    )
    icon_href = (
        f"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 180 180'>"
        f"<rect fill='%23{COMMON['icon_bg_hex']}' width='180' height='180' rx='30'/>"
        f"<text x='90' y='125' text-anchor='middle' font-size='100'>{COMMON['title_emoji']}</text></svg>"
    )
    html = re.sub(r'<link rel="apple-touch-icon" href="[^"]*">',
                  f'<link rel="apple-touch-icon" href="{icon_href}">', html)

    # CSS: scene
    html = re.sub(
        r'background: linear-gradient\(180deg, #2d1b4e 0%, #5d3d8a 25%, #c878a8 45%, #ffb074 58%, #5d8c3e 60%, #4a7a2e 100%\);',
        f'background: {SCENE_GRADIENT};', html
    )
    html = re.sub(r'border-bottom: 4px solid #3d5c1e;', f'border-bottom: {SCENE_BORDER};', html)
    # CSS: grass
    html = re.sub(
        r'background: linear-gradient\(180deg, #5d8c3e 0%, #5d8c3e 35%, #8B6914 35%, #7a5c12 100%\);',
        f'background: {GRASS_BG};', html
    )
    html = re.sub(r'border-right: 1px solid #4a7a2e;', f'border-right: {GRASS_BORDER};', html)
    # CSS: star glow
    html = re.sub(
        r'text-shadow: 0 0 6px #fff, 0 0 10px #c878a8;',
        f'text-shadow: {STAR_SHADOW};', html
    )

    # JS: FURIGANA_DICT
    new_dict = 'const FURIGANA_DICT = ' + json.dumps(furigana, ensure_ascii=False, indent=2) + ';'
    html = replace_block(html, 'const FURIGANA_DICT = {', '};', new_dict)

    # JS: sections
    new_sections = 'const sections = ' + json.dumps(sections, ensure_ascii=False, indent=2) + ';'
    html = replace_block(html, 'const sections = [', '];', new_sections)

    # JS: keys
    html = re.sub(r"const SAVE_KEY = '[^']*';", f"const SAVE_KEY = '{meta['save_key']}';", html)
    html = re.sub(r"const LOG_KEY = '[^']*';", f"const LOG_KEY = '{meta['log_key']}';", html)

    # SPRITES: ユナを don の前に挿入
    yuna_sprite = """  yuna: { // Friend, energetic girl with lapis-colored coat
    width: 12, height: 20,
    pixels: [
      '..TTTTTT....',
      '..TTTTTT....',
      '.TTTTTTTT...',
      '.TSSSSSSTT..',
      '.TSSEESESS..',
      '..SSSSSS....',
      '..SSMMSS....',
      '...LLLL.....',
      '..LLLLLL....',
      '..LSLLSL....',
      '..LSLLSL....',
      '..LLLLLL....',
      '..SLLLLS....',
      '...JJJJ.....',
      '...JJJJ.....',
      '...JJJJ.....',
      '...J..J.....',
      '...J..J.....',
      '..KK..KK....',
      '..KK..KK....',
    ],
    colors: { T:'#8b5a2b', S:'#D4A574', E:'#3B2A14', M:'#C27070', L:'#3a78c8', J:'#1a3050', K:'#3a2410' }
  },
"""
    if 'yuna:' not in html:
        html = html.replace('  don: { // White wolf, horizontal',
                            yuna_sprite + '  don: { // White wolf, horizontal')

    # buildCharacters: ユナ の div を ドン の前に挿入
    yuna_div = """<div class="char-container" id="charYuna">
      <div class="speech" id="speechYuna"></div>
      <div class="char-name">ユナ</div>
      <canvas class="char-sprite" id="canvasYuna"></canvas>
    </div>
    """
    don_div_marker = '<div class="char-container" id="charDon">'
    if 'id="charYuna"' not in html:
        html = html.replace(don_div_marker, yuna_div + don_div_marker)
        html = html.replace(
            "drawSprite('canvasDon', 'don', 3);",
            "drawSprite('canvasYuna', 'yuna', 3);\n  drawSprite('canvasDon', 'don', 3);"
        )

    # UI text
    html = re.sub(r'<h1>[^<]*</h1>', f"<h1>{meta['title_h1']}</h1>", html, count=1)
    html = html.replace(
        '「バイオームの魔法使い」を読んで<br>クイズに答えよう！',
        COMMON['intro_html']
    )
    html = html.replace(
        "'✨ バイオームの魔法使い (前編)クイズ ログ'",
        f"'{meta['log_title']}'"
    )

    meta['output_path'].write_text(html, encoding='utf-8')
    print(f"OK  {meta['output_path'].relative_to(ROOT)}  ({len(html):,} chars)")
    print(f"    sections: {len(sections)}")
    print(f"    questions: {sum(len(s['questions']) for s in sections)}")
    print(f"    furigana entries: {len(furigana)}")


if __name__ == '__main__':
    main()
