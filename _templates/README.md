# やまねこ亭 国語クイズ — テンプレ集

新作を最小手数で追加するためのプロンプト雛型と運用ガイド。

## 全体ワークフロー

```
原作リメイク原稿 (<slug>/原稿.md)
        │
        │  ① quiz-prompt.md を Claude に渡す
        ▼
クイズデータ (sections JSON)
        │
        │  ② html-skeleton-prompt.md を Claude に渡す
        ▼
公開用 HTML (<slug>/index.html or <slug>/partN.html)
```

## ファイル

| ファイル | 役割 | 入力 | 出力 |
|---|---|---|---|
| `quiz-prompt.md` | 物語からクイズデータ生成 | 物語 md | sections の JSON |
| `html-skeleton-prompt.md` | クイズを HTML 化 | sections JSON + メタ | 単体 HTML |

## 既存作品（リファレンス）

| 作品 | 場所 | 規模 | テーマ | 絵文字 |
|---|---|---|---|---|
| ヤマネコ亭 | `1-yamaneko-tei/index.html` | 20 セクション / 40 問 | day（青空） | 🐾 |
| バイオームの魔法使い 前編 | `2-biome-wizard/part1.html` | 13 セクション / 26 問 | night（紫夕暮れ＋星月） | ✨ |
| バイオームの魔法使い 後編 | `2-biome-wizard/part2.html` | 15 セクション / 30 問 | 同上 | ✨ |

## 新作追加の手順

1. 原稿 md を `<新作 slug>/原稿.md` に置く
2. `quiz-prompt.md` を Claude に渡し、原稿から sections JSON を生成
3. セクション数が 25 超なら 5 章境界で part1/part2 に分割を判断
4. `html-skeleton-prompt.md` を Claude に渡し、最新スケルトンから差し替えて HTML を生成
5. ふりがな辞書は fugashi+unidic-lite で再生成（手書きしない）
6. ブラウザで動作確認 → `git commit`

## 過去作からの教訓

- **ふりがな辞書は手書きしない**: 466〜578 語規模になる。fugashi+unidic-lite で生成、明らかな誤読のみ手修正
- **下線は引かない**: バイオームの魔法使い以降の方針。タップで黒い吹き出しのみ
- **SAVE_KEY は HTML 単位で別**: 同じドメイン下でもキーが違えば進捗は独立。**既存ユーザーがプレイ中の HTML の SAVE_KEY は絶対に変えない**
- **タイトル変更時はテキスト中の固有名詞も検索置換**: 「オズ→バイオームの魔法使い」の時、本文・選択肢・解説中の「オズ」「OZ」を全置換する必要があった
- **長文生成時の content-filter エラーは無害**: Claude 側のフィルタが稀に発火。リトライで OK

## スケルトン HTML を流用する理由

ゼロから 2000 行の HTML を生成させると壊れやすい（id 参照や `<br>` を含む `applyFurigana` の細かい挙動が壊れる）。**既存の完成 HTML をコピーし、必要箇所だけ差し替える** のが安全で速い。詳しくは `html-skeleton-prompt.md` を参照。
