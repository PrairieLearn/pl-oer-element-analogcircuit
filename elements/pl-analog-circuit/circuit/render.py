from collections.abc import Iterable
from typing import TypeVar, cast
from .circuit_types import (
    AnalogCircuit,
    Label,
    Pos,
    PosTuple,
    LabelUnion,
    Annotation,
    Component2TermTypes,
    ComponentTypes,
)
import schemdraw
from .helpers import normalize_pos
import schemdraw.elements as elm
from schemdraw.types import BBox
import base64
from math import ceil

E = TypeVar("E", bound=elm.Element)

LOOP_CURRENT_DEFAULT_PAD = 0.3


def draw_label(el: E, label: list[Label] | None) -> E:
    for lbl in label or []:
        el.label(**lbl)
    return el


def normalize_label(label: LabelUnion) -> list[Label]:
    if isinstance(label, str):
        return [{"label": label}]
    elif isinstance(label, dict):
        return [label]
    elif isinstance(label, list):
        if all(isinstance(item, str) for item in label):
            return [{"label": cast(list, label)}]
        else:
            return [item for sub_label in label for item in normalize_label(sub_label)]
    else:
        return []


def to_drawing_pos(pos: PosTuple, unit: float) -> tuple[float, float]:
    return (pos[0] * unit, pos[1] * unit)


def label_side_to_loc(from_: PosTuple, to: PosTuple, side: str) -> str:
    if abs(to[1] - from_[1]) > abs(to[0] - from_[0]):
        if side == "right":
            return "bottom"
        if side == "left":
            return "top"
    return side


def orient_labels(
    from_: PosTuple, to: PosTuple, label: list[Label] | None
) -> list[Label]:
    oriented_labels = []
    for lbl in label or []:
        oriented_label = dict(lbl)
        side = oriented_label.pop("side", None)
        if side is not None and "loc" not in oriented_label:
            oriented_label["loc"] = label_side_to_loc(from_, to, str(side))
        oriented_labels.append(cast(Label, oriented_label))
    return oriented_labels


def validation(from_, to, type):
    if type != "Line":
        (fx, fy) = from_
        (tx, ty) = to
        if abs(fx - tx) > 1 or abs(fy - ty) > 1:
            return "Warning: " + type + " crosses multiple grids"


def draw_component(
    from_: PosTuple,
    to: PosTuple,
    *,
    unit: float,
    type: Component2TermTypes = "Line",
    label: list[Label] | None = None,
    annotations: list[Annotation] | None = None,  # TODO
) -> elm.Element2Term:
    (fx, fy) = from_
    (tx, ty) = to
    validation(from_, to, type)

    el: elm.Element2Term = getattr(elm, type)()
    el = draw_label(el, orient_labels(from_, to, label))
    el.endpoints(to_drawing_pos(from_, unit), to_drawing_pos(to, unit))
    return el


def draw_single_component(
    pos: PosTuple,
    *,
    unit: float,
    type: ComponentTypes = "Ground",
    label: list[Label] | None = None,
    annotations: list[Annotation] | None = None,  # TODO
) -> elm.Element2Term:
    el: elm.Element2Term = getattr(elm, type)()
    el = draw_label(el, label)
    el.at(to_drawing_pos(pos, unit))
    return el


class FakeElement:
    def __init__(self, bbox: BBox):
        self.bbox = bbox

    def get_bbox(self, *args, **kwargs) -> BBox:
        return self.bbox


def bbox_from_points(points: Iterable[PosTuple]) -> BBox:
    points = list(points)
    if not points:
        raise ValueError("points list is empty")
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return BBox(min(xs), min(ys), max(xs), max(ys))


def render_circuit(
    circuit: AnalogCircuit, *, scale: float = 1.0, debug: bool = False
) -> str:
    """Render an analog circuit.

    This function takes an AnalogCircuit object and returns a base64 data URL of the rendered circuit image.

    Args:
        circuit (AnalogCircuit): The circuit to render.

    Returns:
        str: A base64 data URL of the rendered circuit image.
    """
    nx = 0
    ny = 0

    node_aliases: dict[str, PosTuple] = {}

    def get_pos(pos: Pos) -> PosTuple:
        if isinstance(pos, str) and pos in node_aliases:
            return node_aliases[pos]
        x, y = normalize_pos(pos)
        return (x * scale, y * scale)

    for node in circuit.get("nodes", []):
        if "name" in node:
            node_aliases[node["name"]] = get_pos(normalize_pos(node["pos"]))

    with schemdraw.Drawing(show=False) as d:
        last_to = (0, 0)
        assert d.unit is not None, "schemdraw Drawing unit is None"
        for edge in circuit.get("components", []):
            if "to" in edge:
                # default from is the last to position or (0,0)
                from_node = get_pos(edge.get("from", last_to or (0, 0)))
                last_to = to_node = get_pos(edge["to"])
                type = edge.get("type", "Line")
                label = normalize_label(edge.get("label", []))
                annotations = edge.get("annotations", [])
                comp = draw_component(
                    from_node,
                    to_node,
                    type=type,
                    unit=d.unit,
                    label=label,
                    annotations=annotations,
                )
                nx = max(nx, to_node[0], from_node[0])
                ny = max(ny, to_node[1], from_node[1])

                if "annotations" in edge:
                    for annotation in edge["annotations"]:
                        if annotation["type"] == "CurrentLabel":
                            el = elm.CurrentLabel(
                                top=annotation.get("top", None),
                                ofst=annotation.get("ofst", None),
                                reverse=annotation.get("reverse", None),
                            ).at(comp)  # type: ignore # schemdraw typing issue
                            if "label" in annotation:
                                label = normalize_label(annotation["label"])
                                draw_label(el, label)

            elif "pos" in edge:
                pos = get_pos(edge["pos"])
                type = edge.get("type", "Ground")
                label = normalize_label(edge.get("label", []))
                annotations = edge.get("annotations", [])
                draw_single_component(
                    pos, type=type, unit=d.unit, label=label, annotations=annotations
                )
                nx = max(nx, pos[0])
                ny = max(ny, pos[1])

        for node in circuit.get("nodes", []):
            pos = get_pos(node["pos"])
            dpos = to_drawing_pos(pos, unit=d.unit)
            if "dot" in node:
                elm.Dot(open=node["dot"] != "filled").at(dpos)
            if "label" in node:
                # TODO: make this customizable, default to check top otherwise top-left
                label = elm.Element().label(node["label"], ofst=(0.2, 0))
            nx = max(nx, pos[0])
            ny = max(ny, pos[1])

        for annotation in circuit.get("annotations", []):
            if annotation["type"] == "LoopCurrent":
                assert "bounds" in annotation, "LoopCurrent annotation missing bounds"
                bounds = annotation["bounds"]
                points = [to_drawing_pos(get_pos(pos), unit=d.unit) for pos in bounds]
                bbox = bbox_from_points(points)
                # swap min and max
                bbox = BBox(bbox.xmax, bbox.ymax, bbox.xmin, bbox.ymin)
                pad = annotation.get("pad", LOOP_CURRENT_DEFAULT_PAD) * d.unit
                el = elm.LoopCurrent(
                    elm_list=[cast(elm.Element, FakeElement(bbox))] * 4, pad=pad
                )
                if "label" in annotation:
                    label = normalize_label(annotation["label"])
                    draw_label(el, label)

        if debug:
            for i in range(ceil(nx) + 1):
                for j in range(ceil(ny) + 1):
                    pos = to_drawing_pos((i, j), unit=d.unit)
                    elm.Label(str(i) + "," + str(j)).at(pos).color("red")

        img_bytes = d.get_imagedata()
        data_url = "data:image/svg+xml;base64," + base64.b64encode(img_bytes).decode(
            "utf-8"
        )
        return data_url
