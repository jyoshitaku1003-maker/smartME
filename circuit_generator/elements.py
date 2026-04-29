import schemdraw.elements as elm
from schemdraw.elements.elements import Element2Term, gap
from schemdraw.elements.twoterm import resheight
from schemdraw.elements.sources import batw, bat1, bat2
from schemdraw.segments import Segment, SegmentCircle, SegmentPoly


class BatteryCW(Element2Term):
    """Single cell battery: negative(short) at start, positive(long) at end.
    When direction=up, + is at top → clockwise conventional current."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.segments.append(Segment([(0, 0), gap, (batw, 0)]))
        self.segments.append(Segment([(0, bat2), (0, -bat2)]))    # short = negative
        self.segments.append(Segment([(batw, bat1), (batw, -bat1)]))  # long = positive


_cx = resheight * 1.4   # cathode x position (same as schemdraw Diode)
_bend = resheight * 0.6  # right-angle bend length


class ZenerSingle(Element2Term):
    """Zener diode: cathode bar with one right-angle bend at the bottom only."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Lead lines and cathode bar (same as Diode)
        self.segments.append(Segment([(0, 0), gap, (_cx, resheight),
                                      (_cx, -resheight), gap, (_cx, 0)]))
        # Diode triangle
        self.segments.append(SegmentPoly([(0, resheight), (_cx, 0), (0, -resheight)]))
        # Single right-angle bend at bottom of cathode bar
        self.segments.append(Segment([(_cx, -resheight), (_cx - _bend, -resheight)]))


_r = 0.18   # open-circle radius
_len = 3.0  # total element length


class VoltageDiff(Element2Term):
    """Voltage annotation: white open circles at each end with an arrow between them.
    Arrow points toward positive terminal (end)."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Arrow line between the two circles (with gap so it doesn't overlap circles)
        self.segments.append(Segment([(_r, 0), (_len - _r, 0)],
                                     arrow='->', arrowwidth=0.18, arrowlength=0.3))
        # Open circles at each terminal
        self.segments.append(SegmentCircle((0, 0), _r, fill='white'))
        self.segments.append(SegmentCircle((_len, 0), _r, fill='white'))


# Maps YAML type names → schemdraw element classes
ELEMENT_MAP: dict[str, type] = {
    # 受動素子
    "resistor":          elm.ResistorIEC,
    "capacitor":         elm.Capacitor,
    "inductor":          elm.Inductor2,
    "resistor_variable": elm.ResistorVarIEC,

    # 電源
    "source_ac":         elm.SourceSin,
    "battery":           BatteryCW,

    # 半導体
    "diode":             elm.Diode,
    "zener":             ZenerSingle,
    "led":               elm.LED,
    "photodiode":        elm.Photodiode,
    "transistor_npn":    elm.BjtNpn,
    "transistor_pnp":    elm.BjtPnp,
    "mosfet_n":          elm.NMos,
    "mosfet_p":          elm.PMos,
    "jfet_n":            elm.JFetN,
    "jfet_p":            elm.JFetP,
    "opamp":             lambda **kw: elm.Opamp(leads=True, **kw),

    # 計測器
    "ammeter":           elm.MeterA,
    "voltmeter":         elm.MeterV,

    # 接続・補助
    "ground":            elm.Ground,
    "ground_chassis":    elm.GroundChassis,
    "switch":            elm.Switch,
    "transformer":       elm.Transformer,
    "line":              elm.Line,
    "dot":               elm.Dot,
    "arrow":             elm.Arrow,
    "voltage_diff":      VoltageDiff,
}

# Optional elements (may not exist in all schemdraw versions)
for _name, _attr in [("fuse", "Fuse")]:
    _cls = getattr(elm, _attr, None)
    if _cls is not None:
        ELEMENT_MAP[_name] = _cls

ELEMENT_NAMES_JA: dict[str, str] = {
    "resistor":          "抵抗 (R)",
    "capacitor":         "コンデンサ (C)",
    "inductor":          "コイル・インダクタ (L)",
    "resistor_variable": "可変抵抗",
    "source_ac":         "交流電源（正弦波）",
    "battery":           "電池・単セル (E)",
    "diode":             "ダイオード (D)",
    "zener":             "ツェナーダイオード",
    "led":               "LED（発光ダイオード）",
    "photodiode":        "フォトダイオード",
    "transistor_npn":    "NPN バイポーラトランジスタ",
    "transistor_pnp":    "PNP バイポーラトランジスタ",
    "mosfet_n":          "N チャネル MOSFET",
    "mosfet_p":          "P チャネル MOSFET",
    "jfet_n":            "N チャネル JFET",
    "jfet_p":            "P チャネル JFET",
    "opamp":             "オペアンプ（演算増幅器）",
    "ammeter":           "電流計 (A)",
    "voltmeter":         "電圧計 (V)",
    "ground":            "アース・接地 (GND)",
    "ground_chassis":    "シャーシアース",
    "switch":            "スイッチ (SW)",
    "fuse":              "ヒューズ",
    "transformer":       "変圧器・トランス (T)",
    "line":              "配線",
    "dot":               "接続点（ジャンクション）",
    "arrow":             "矢印",
    "voltage_diff":      "電位差・電圧表記 (V)",
}
