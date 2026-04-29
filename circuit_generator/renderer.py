"""YAML circuit description → schemdraw → SVG"""

import warnings
from pathlib import Path
from typing import Union

import schemdraw
import schemdraw.elements as elm
import yaml

from .elements import ELEMENT_MAP

schemdraw.use("svg")


def _build_element(item: dict):
    """Convert one YAML item dict into a configured schemdraw element."""
    elem_type = item["type"]
    cls = ELEMENT_MAP.get(elem_type)
    if cls is None:
        warnings.warn(f"Unknown element type: {elem_type!r} — skipping")
        return None

    e = cls()

    direction = item.get("direction", "right")
    e = {"up": e.up, "down": e.down, "left": e.left, "right": e.right}.get(
        direction, e.right
    )()

    if "length" in item:
        e = e.length(float(item["length"]))

    if "label" in item:
        loc = item.get("label_loc", "")
        e = e.label(item["label"], loc=loc) if loc else e.label(item["label"])

    if "value" in item:
        e = e.label(item["value"], loc=item.get("value_loc", "bottom"))

    return e


def circuit_to_svg(
    data: dict,
    output_path: Union[str, Path, None] = None,
) -> str:
    """Render a circuit dict to an SVG string (and optionally save to file)."""
    with schemdraw.Drawing() as d:
        for item in data.get("circuit", []):
            t = item.get("type", "")
            if t == "push":
                d.push()
            elif t == "pop":
                d.pop()
            elif t == "dot":
                d.add(elm.Dot())
            elif t in ELEMENT_MAP:
                elem = _build_element(item)
                if elem is not None:
                    d.add(elem)

    if output_path:
        d.save(str(output_path))

    return d.get_imagedata("svg").decode("utf-8")


def yaml_to_svg(
    yaml_path: Union[str, Path],
    output_path: Union[str, Path, None] = None,
) -> str:
    """Load a YAML circuit file and render it to SVG."""
    try:
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except UnicodeDecodeError:
        with open(yaml_path, encoding="cp932") as f:
            data = yaml.safe_load(f)
    return circuit_to_svg(data, output_path)
