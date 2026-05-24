# HTML 化プロンプト（スケルトン差し替え方式）

> このファイルの内容を Claude にペーストし、続けて sections JSON とメタ情報を貼ると、差し替え済み HTML が返ってくる想定。

---

## 方針

HTML をゼロから生成せず、**最新の完成 HTML をスケルトンとしてコピーし、特定箇所だけ差し替える**。これにより:
- 既存のレイアウト・ふりがな実装・ゲームロジックを壊さない
- 差分が小さくレビューしやすい
- 2000 行の HTML 全文を再生成する際の崩壊リスクを回避

## スケルトンの選択

| 用途 | 推奨スケルトン |
|---|---|
| Day テーマ（明るい昼空） | `1-yamaneko-tei/index.html` |
| Night テーマ（紫夕暮れ・星・月） | `2-biome-wizard/part1.html` |

スケルトンファイルを丸ごとコピーしてから、以下の差し替えを行う。

## 入力

### 1. クイズデータ
`quiz-prompt.md` で生成した `sections` 配列の JSON。

### 2. メタ情報
| キー | 例 | 備考 |
|---|---|---|
| `slug` | `wizard` / `new-story` | フォルダ名 |
| `output_path` | `wizard/part1.html` | リポ内の出力先 |
| `app_title` | `バイオームの魔法使い (前編) 国語クイズ` | `<title>` |
| `mobile_title` | `やまねこ亭` | ホーム画面短縮名 |
| `title_emoji` | `✨` / `🐾` | アイコン絵文字 |
| `icon_bg_color` | `#5a3a1a` | アイコン背景 hex |
| `theme` | `day` / `night` | スケルトン選択を兼ねる |
| `save_key` | `wizard_part1_save` | **既存と絶対衝突させない** |
| `log_key` | `wizard_part1_save_log` | save_key + `_log` |

## 差し替え箇所

スケルトンの以下を**全て**置換する。1 つでも見落とすと既存進捗を壊す or 表示が崩れる。

### A. head 内のメタ情報

```html
<meta name="apple-mobile-web-app-title" content="{mobile_title}">
<link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 180 180'><rect fill='%23{icon_bg_color_no_hash}' width='180' height='180' rx='30'/><text x='90' y='125' text-anchor='middle' font-size='100'>{title_emoji}</text></svg>">
<title>{app_title}</title>
```

注: `icon_bg_color` の `#` は SVG 内では `%23` にエスケープ。

### B. SAVE_KEY / LOG_KEY（script 内）

```js
const SAVE_KEY = '{save_key}';
const LOG_KEY = '{log_key}';
```

### C. sections 配列

`const sections = [...]` を `quiz-prompt.md` の出力で**全置換**。

### D. ふりがな辞書

`const FURIGANA_DICT = { ... }` を新作の本文から再生成して全置換。生成方法は次節。

### E. テーマ要素

- **night** にする場合: `2-biome-wizard/part1.html` をスケルトンに使えば紫グラデーション・星・月・紫衣装が既に組み込まれている
- **day** にする場合: `1-yamaneko-tei/index.html` をスケルトンに使えば青空・通常衣装が既に組み込まれている
- 中間（夕焼け、雪原など）の新テーマが必要な場合は `.scene` の `background: linear-gradient(...)` と `SPRITES.yuuki/kent.colors` を編集

### F. タイトル画面のテキスト（必要に応じて）

スケルトンの `renderTitle()` 周辺の以下を作品名に合わせる:
- 作品名見出し
- サブタイトル（`〜 国語クイズ 〜` など）
- セクション数・問題数の説明

## ふりがな辞書の生成

```bash
# Jetson 上で実行（要 fugashi + unidic-lite）
# pip install fugashi[unidic-lite]

python3 <<'EOF'
import json, re, sys
from fugashi import Tagger

# sections JSON を読む（本文・問題文・選択肢・解説すべてから語を集める）
sections = json.load(open('sections.json'))
buf = []
for s in sections:
    buf.append(s['text'])
    for q in s['questions']:
        buf.append(q['q'])
        buf.extend(q['choices'])
        buf.append(q['explanation'])
text = '\n'.join(buf)

t = Tagger()
out = {}
for w in t(text):
    surface = w.surface
    if not re.search(r'[一-龯々]', surface): continue   # 漢字含まない語はスキップ
    if len(surface) > 8: continue
    kana = (w.feature.kana or '').strip()
    if not kana or kana == '*': continue
    # カタカナ → ひらがな
    hira = ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in kana)
    out[surface] = hira

print(json.dumps(out, ensure_ascii=False, indent=2))
EOF
```

辞書化のポイント:
- 小3以上の漢字を含む語のみ
- 同じ語は 1 エントリ。長い語が先にマッチするよう `applyFurigana` 側でソート済（変更不要）
- 生成後、明らかな誤読は手で修正（過去例: 「並べて→なべて」を「ならべて」に）

## ビルド後の検証チェックリスト

ローカル（`file://` で直接開く or `python3 -m http.server`）で:

- [ ] タイトル画面で「はじめから」が動く
- [ ] 1 問正解 → 次の質問へ進む
- [ ] 1 問間違い → エラー表示、進めない（正解必須化）
- [ ] 「もう一度読む」で本文に戻る
- [ ] 漢字タップでふりがな吹き出しが出る、外側タップで閉じる
- [ ] リロード後タイトル画面で「つづきから（章名）」が出る
- [ ] DevTools の Application > Local Storage で `SAVE_KEY` の存在確認
- [ ] 既存作品の `SAVE_KEY` と衝突していない
- [ ] iOS Safari でホーム画面追加 → アイコンが想定の絵文字

## アンチパターン

- **スケルトンの HTML 構造（id 名、class 名）を変えない**: ゲームロジックが id 参照しているため
- **`applyFurigana` 関数のロジックを変えない**: `<br>` を一時マーカーで保護する細工が入っている
- **`SPRITES` のキー（`yuuki/kent/don`）を変えない**: `buildCharacters` が固定参照
- **辞書を手で大量編集しない**: fugashi 再生成のほうが速くて正確
- **既存 HTML の `SAVE_KEY` を変更しない**: 既存ユーザーの進捗が消える

## 出力

差し替え後の HTML を**コードブロックで全文**返す。差分形式ではなくフルファイルが望ましい（コピペで `<slug>/<file>.html` に保存できる形）。
