"""Natural language → YAML circuit description (via OpenAI API) → SVG"""

import re
from pathlib import Path
from typing import Union

import yaml
from openai import OpenAI

from .renderer import circuit_to_svg

_SYSTEM_PROMPT = """\
あなたは電気回路をYAML形式に変換する専門家です。
臨床工学技士国家試験に出題される電気回路を対象とします。

## 利用可能な素子タイプ

| type | 日本語名 |
|------|---------|
| resistor | 抵抗 (R) |
| capacitor | コンデンサ (C) |
| inductor | コイル (L) |
| source_dc | 直流電圧源 |
| source_ac | 交流電源（正弦波）|
| source_current | 電流源 (I) |
| battery | 電池 |
| diode | ダイオード |
| zener | ツェナーダイオード |
| led | LED |
| photodiode | フォトダイオード |
| transistor_npn | NPN バイポーラトランジスタ |
| transistor_pnp | PNP バイポーラトランジスタ |
| jfet_n | N チャネル JFET |
| jfet_p | P チャネル JFET |
| opamp | オペアンプ |
| ammeter | 電流計 |
| voltmeter | 電圧計 |
| ground | アース (GND) |
| switch | スイッチ |
| transformer | 変圧器 |
| line | 配線 |
| dot | 接続点 |
| push | 分岐点保存（並列回路用）|
| pop | 分岐点復元（並列回路用）|

## YAMLスキーマ

```yaml
title: "回路名"
description: "説明（任意）"
circuit:
  - type: [素子タイプ]   # 必須
    label: "ラベル"      # 任意
    direction: right     # up / down / left / right（デフォルト: right）
    length: 3            # 任意（デフォルト: 3）
```

## 描画ルール

- 各素子は前の素子の終端から連続して描画される（直列接続）
- ループを閉じるには line で始点に戻る
- 並列接続: push で現在位置を保存 → 一方の枝 → pop で位置復元 → もう一方の枝

## 電源の選択ルール

- 「交流」と明示されている場合のみ `source_ac` を使用する
- それ以外（「直流」「電池」または電源種別の指定なし）は `battery` を使用する

## 例1: RC直列回路

```yaml
title: "RC直列回路"
circuit:
  - type: battery
    label: "V"
    direction: up
  - type: resistor
    label: "R"
    direction: right
  - type: capacitor
    label: "C"
    direction: down
  - type: line
    direction: left
```

## 例2: RC並列回路

```yaml
title: "RC並列回路"
circuit:
  - type: battery
    label: "V"
    direction: up
  - type: line
    direction: right
  - type: push
  - type: resistor
    label: "R"
    direction: down
  - type: line
    direction: left
  - type: pop
  - type: line
    direction: right
  - type: capacitor
    label: "C"
    direction: down
  - type: line
    direction: left
```

## 例3: RLC直列回路

```yaml
title: "RLC直列回路"
circuit:
  - type: battery
    label: "V"
    direction: up
  - type: resistor
    label: "R"
    direction: right
  - type: inductor
    label: "L"
    direction: right
  - type: capacitor
    label: "C"
    direction: down
  - type: line
    direction: left
  - type: line
    direction: left
```

## 例4: RC直列回路（交流）

```yaml
title: "RC直列回路（交流）"
circuit:
  - type: source_ac
    label: "V"
    direction: up
  - type: resistor
    label: "R"
    direction: right
  - type: capacitor
    label: "C"
    direction: down
  - type: line
    direction: left
```

YAMLコードブロック（```yaml ... ```）のみを返してください。説明文は不要です。\
"""


def nl_to_yaml(
    description: str,
    client: OpenAI | None = None,
) -> dict:
    """Convert natural language circuit description to a circuit dict."""
    if client is None:
        client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": f"次の回路をYAMLで表現してください: {description}"},
        ],
        temperature=0,
    )

    raw = response.choices[0].message.content
    m = re.search(r"```(?:yaml)?\n(.*?)\n```", raw, re.DOTALL)
    yaml_str = m.group(1) if m else raw
    return yaml.safe_load(yaml_str)


def nl_to_svg(
    description: str,
    output_path: Union[str, Path, None] = None,
    client: OpenAI | None = None,
) -> str:
    """One-shot: natural language → SVG string (optionally saved to file)."""
    data = nl_to_yaml(description, client)
    return circuit_to_svg(data, output_path)
