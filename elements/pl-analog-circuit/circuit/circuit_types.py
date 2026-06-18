from typing import TypedDict, Literal, TypeAlias
from typing_extensions import NotRequired
from schemdraw.types import LabelLoc, Halign, Valign

Numeric: TypeAlias = float | int


class PosDict(TypedDict):
    x: Numeric
    y: Numeric


PosTuple: TypeAlias = tuple[Numeric, Numeric]

Pos: TypeAlias = PosDict | PosTuple | str

Component2TermTypes: TypeAlias = Literal['Resistor', 'ResistorIEEE', 'ResistorIEC', 'ResistorVar', 'ResistorVarIEEE', 'ResistorVarIEC', 'Thermistor', 'Photoresistor', 'PhotoresistorIEEE', 'PhotoresistorIEC', 'Rshunt', 'Capacitor', 'Capacitor2', 'CapacitorVar', 'CapacitorTrim', 'Diode', 'Schottky', 'DiodeTunnel', 'DiodeShockley', 'Zener', 'DiodeTVS', 'Varactor', 'LED', 'LED2', 'Photodiode', 'Potentiometer', 'PotentiometerIEEE', 'PotentiometerIEC', 'Diac', 'Triac', 'SCR', 'Memristor', 'Memristor2', 'Josephson', 'Fuse', 'FuseUS', 'FuseIEEE', 'FuseIEC', 'Inductor', 'Inductor2', 'Crystal', 'Breaker', 'CPE', 'SparkGap', 'RBox', 'RBoxVar', 'PotBox', 'PhotoresistorBox', 'Nullator', 'Norator', 'CurrentMirror', 'VoltageMirror', 'Source', 'SourceV', 'SourceI', 'SourceSin', 'SourcePulse', 'SourceSquare', 'SourceTriangle', 'SourceRamp', 'SourceControlled', 'SourceControlledV', 'SourceControlledI', 'BatteryCell', 'Battery', 'MeterV', 'MeterI', 'MeterA', 'MeterOhm', 'Lamp', 'Lamp2', 'Solar', 'Neon', 'Switch', 'SwitchSpdt', 'Button', 'SwitchReed', 'Bjt2', 'BjtNpn2', 'BjtPnp2', 'BjtPnp2c2', 'NFet2', 'PFet2', 'JFet2', 'JFetN2', 'JFetP2', 'NMos2', 'PMos2', 'Motor', 'Coax', 'Triax', 'Line', 'DataBusLine', 'Arrow', 'Gap', 'BusLine']

ComponentTypes: TypeAlias = Literal[
    'Ground',
    'GroundSignal',
    'GroundChassis',
    'Vss',
    'Vdd',
]

UnitTypes: TypeAlias = Literal['Ohms', 'Volts', 'Watts', 'Amperes', 'Power']

PrefixTypes: TypeAlias = Literal['nano', 'micro', 'milli', 'centi', 'deci', 'unit', 'kilo', 'mega', 'giga', 'tera']


# see schemdraw.elements.Element's label method
class Label(TypedDict):
    label: str | list[str]
    loc: NotRequired[LabelLoc]
    side: NotRequired[Literal['top', 'bottom', 'left', 'right']]
    ofst: NotRequired[PosTuple | float | None]
    halign: NotRequired[Halign]
    valign: NotRequired[Valign]
    rotate: NotRequired[bool | float]
    fontsize: NotRequired[float]
    font: NotRequired[str]
    mathfont: NotRequired[str]
    color: NotRequired[str]
    href: NotRequired[str]
    decoration: NotRequired[str]


LabelUnion: TypeAlias = list[str | Label] | str | Label


class Annotation(TypedDict):
    type: Literal['CurrentLabel', 'LoopCurrent']  # 'CurrentLabel', add more
    label: NotRequired[LabelUnion]
    # for current label
    top: NotRequired[bool]
    ofst: NotRequired[Numeric]
    reverse: NotRequired[bool]
    # for loop current
    bounds: NotRequired[list[Pos]]
    pad: NotRequired[Numeric]


class Node(TypedDict):
    pos: Pos
    name: NotRequired[str]
    dot: NotRequired[Literal['open', 'filled'] | bool]
    label: NotRequired[str]
    value: NotRequired[Numeric]
    unit: NotRequired[UnitTypes]
    siprefixval: NotRequired[PrefixTypes | list[PrefixTypes]]  # default: 'unit'
    solve: NotRequired[list[UnitTypes]]
    name: NotRequired[str]
    siprefixans: NotRequired[list[PrefixTypes]]  # default: 'unit'


# this uses the function declaration to bypass the hard python keyword 'from'
# names such as r"\d\d", r"\d+,\d+" for the from and to keys implicitly refers
# to nodes at those positions in the circuit grid
Component2Term = TypedDict('Component2Term', {
    # if `from` is not specified, its default to (0,0) if its the first item
    # or the last `to` position
    'from': NotRequired[Pos],  # format is "x,y" or (x,y)
    'to': Pos,   # format is "x,y" or (x,y)
    'type': NotRequired[Component2TermTypes],  # default: 'Wire'
    'label': NotRequired[LabelUnion],
    'annotations': NotRequired[list[Annotation]],
    'value': NotRequired[Numeric],
    'unit': NotRequired[UnitTypes],
    'siprefixval': NotRequired[PrefixTypes | list[PrefixTypes]],  # default: 'unit'
    'solve': NotRequired[list[UnitTypes]],
    'name': NotRequired[str],
    'siprefixans': NotRequired[list[PrefixTypes]],  # default: 'unit'
})


class Component(TypedDict):
    # if `pos` is not specified, its default to (0,0) if its the first item
    # or the last `to` position
    pos: NotRequired[Pos]
    type: ComponentTypes
    label: NotRequired[LabelUnion]
    annotations: NotRequired[list[Annotation]]
    value: NotRequired[Numeric]
    unit: NotRequired[UnitTypes]
    siprefixval: NotRequired[PrefixTypes | list[PrefixTypes]]  # default: 'unit'
    solve: NotRequired[list[UnitTypes]]
    name: NotRequired[str]
    siprefixans: NotRequired[list[PrefixTypes]]  # default: 'unit'


class AnalogCircuit(TypedDict):
    nodes: NotRequired[list[Node]]
    components: list[Component | Component2Term]
    annotations: NotRequired[list[Annotation]]
