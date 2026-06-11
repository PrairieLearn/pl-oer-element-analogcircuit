from circuit import AnalogCircuit


def generate(data):
    schematic: AnalogCircuit = {
        "components": [
            {"from": "0,0", "to": (0, 4), "type": "SourceV", "label": "$V_S$"},
            {"to": "3,4", "type": "Resistor", "label": {"label": "$R_1$", "loc": "bottom"} , "annotations": [{"type": "CurrentLabel", "label": "$I_1$", "top": False, "reverse": True, "ofst": 0.5}], "value": 3, "unit": "Ohms", "siprefixval": ["kilo"], "solve": ["Volts", "Amperes"], "name": "R1", "siprefixans": ["milli"]},
            {"from": "0,0", "to": "4,0"},
            {"from": "2,0", "to": "2,2", "type": "Resistor", "label": "$R_3", "value": 6, "unit": "Ohms", "siprefixval": "kilo"},
            {"from": "2,2", "to": "4,2"},
            {"from": "3,2", "to": "3,4", "type": "Resistor", "label": "$R_2$", "value": 5, "unit": "Ohms", "siprefixval": "kilo"},
            {"from": "4,0", "to": "4,2", "type": "SourceI", "label": "$I_S$"},
            {"pos": "2,0", "type": "Ground"}
        ],
        "nodes": [
            {"pos": "0,4", "dot": "filled", "label": "a", "value": 18, "unit": "Volts"},
            {"pos": "3,4", "dot": "open", "label": "b", "value": 14.4, "unit": "Volts"},
            {"pos": "3,2", "dot": "filled", "label": "c", "value": 8.4, "unit": "Volts", "siprefixval": "kilo"}
        ],
        "annotations": [
            {"type": "LoopCurrent", "bounds": [(2, 2), (4, 0)], "pad": 0.4, "label": "$I_{loop}$"}
        ]
    }
    params = data['params'].setdefault('circuit1', {})
    params['circuit'] = schematic
