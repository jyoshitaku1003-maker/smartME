import schemdraw.elements as elm
from schemdraw.elements.elements import Element2Term, gap
from schemdraw.elements.sources import batw, bat1, bat2
from schemdraw.segments import Segment


class BatteryCW(Element2Term):
    """Single cell battery: negative(short) at start, positive(long) at end.
    When direction=up, + is at top → clockwise conventional current."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.segments.append(Segment([(0, 0), gap, (batw, 0)]))
        self.segments.append(Segment([(0, bat2), (0, -bat2)]))    # short = negative
        self.segments.append(Segment([(batw, bat1), (batw, -bat1)]))  # long = positive


# Maps YAML type names → schemdraw element classes
ELEMENT_MAP: dict[str, type] = {
    # 受動素子
    "resistor":          elm.ResistorIEC,
    "capacitor":         elm.Capacitor,
    "inductor":          elm.Inductor2,
    "resistor_variable": elm.RBox,

    # 電源
    "source_dc":         elm.SourceV,
    "source_ac":         elm.SourceSin,
    "source_current":    elm.SourceI,
    "battery":           BatteryCW,

    # 半導体
    "diode":             elm.Diode,
    "zener":             elm.Zener,
    "led":               elm.LED,
    "photodiode":        elm.Photodiode,
    "transistor_npn":    elm.BjtNpn,
    "transistor_pnp":    elm.BjtPnp,
    "jfet_n":            elm.JFetN,
    "jfet_p":            elm.JFetP,
    "opamp":             elm.Opamp,

    # 計測器
    "ammeter":           elm.MeterA,
    "voltmeter":         elm.MeterV,

    # 接続・補助
    "ground":            elm.Ground,
    "ground_signal":     elm.GroundSignal,
    "ground_chassis":    elm.GroundChassis,
    "switch":            elm.Switch,
    "transformer":       elm.Transformer,
    "line":              elm.Line,
    "dot":               elm.Dot,
    "arrow":             elm.Arrow,
}

# Optional elements (may not exist in all schemdraw versions)
for _name, _attr in [("fuse", "Fuse"), ("lamp", "Lamp")]:
    _cls = getattr(elm, _attr, None)
    if _cls is not None:
        ELEMENT_MAP[_name] = _cls

ELEMENT_NAMES_JA: dict[str, str] = {
    "resistor":          "抵抗 (R)",
    "capacitor":         "コンデンサ (C)",
    "inductor":          "コイル・インダクタ (L)",
    "resistor_variable": "可変抵抗",
    "source_dc":         "直流電圧源",
    "source_ac":         "交流電源（正弦波）",
    "source_current":    "電流源 (I)",
    "battery":           "電池・単セル (E)",
    "diode":             "ダイオード (D)",
    "zener":             "ツェナーダイオード",
    "led":               "LED（発光ダイオード）",
    "photodiode":        "フォトダイオード",
    "transistor_npn":    "NPN バイポーラトランジスタ",
    "transistor_pnp":    "PNP バイポーラトランジスタ",
    "jfet_n":            "N チャネル JFET",
    "jfet_p":            "P チャネル JFET",
    "opamp":             "オペアンプ（演算増幅器）",
    "ammeter":           "電流計 (A)",
    "voltmeter":         "電圧計 (V)",
    "ground":            "アース・接地 (GND)",
    "ground_signal":     "シグナルアース",
    "ground_chassis":    "シャーシアース",
    "switch":            "スイッチ (SW)",
    "fuse":              "ヒューズ",
    "lamp":              "電球・ランプ",
    "transformer":       "変圧器・トランス (T)",
    "line":              "配線",
    "dot":               "接続点（ジャンクション）",
    "arrow":             "矢印",
}
