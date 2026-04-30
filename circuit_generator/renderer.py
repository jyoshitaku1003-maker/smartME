"""YAML circuit description → schemdraw → SVG"""

import warnings
from pathlib import Path
from typing import Union

import schemdraw
import schemdraw.elements as elm
import yaml

from .elements import ELEMENT_MAP

schemdraw.use("svg")


def _build_element(item: dict, named: dict):
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

    # tox/toy: extend element to the x/y coordinate of a named anchor
    for field, method in (("tox", "tox"), ("toy", "toy")):
        ref = item.get(field)
        if ref and isinstance(ref, list) and len(ref) == 2:
            ref_id, anchor = ref
            ref_elem = named.get(ref_id)
            if ref_elem is not None:
                e = getattr(e, method)(getattr(ref_elem, anchor))
            else:
                warnings.warn(f"Unknown element id in {field}: {ref_id!r}")

    if "label" in item:
        loc = item.get("label_loc", "")
        e = e.label(item["label"], loc=loc) if loc else e.label(item["label"])

    if "value" in item:
        e = e.label(item["value"], loc=item.get("value_loc", "bottom"))

    if item.get("idot"):
        e = e.idot()

    if item.get("dot"):
        e = e.dot()

    return e


def circuit_to_svg(
    data: dict,
    output_path: Union[str, Path, None] = None,
) -> str:
    """Render a circuit dict to an SVG string (and optionally save to file)."""
    named: dict[str, object] = {}  # id → added schemdraw element

    with schemdraw.Drawing() as d:
        for item in data.get("circuit", []):
            t = item.get("type", "")
            if t == "push":
                d.push()
                continue
            elif t == "pop":
                d.pop()
                continue

            # Resolve at: [id, anchor] for positioning
            at = item.get("at")
            at_point = None
            if at and isinstance(at, list) and len(at) == 2:
                ref_id, anchor = at
                ref_elem = named.get(ref_id)
                if ref_elem is not None:
                    at_point = getattr(ref_elem, anchor)
                else:
                    warnings.warn(f"Unknown element id: {ref_id!r}")

            if t == "dot":
                dot = elm.Dot()
                if at_point is not None:
                    dot = dot.at(at_point)
                added = d.add(dot)
            elif t not in ELEMENT_MAP:
                continue
            else:
                elem = _build_element(item, named)
                if elem is None:
                    continue
                if at_point is not None:
                    elem = elem.at(at_point)
                added = d.add(elem)

            elem_id = item.get("id")
            if elem_id:
                named[elem_id] = added

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
