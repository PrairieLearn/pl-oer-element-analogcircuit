def generate(data):
    data["correct_answers"]["volt"] = 2.7

    schematic = {
        "components": [
            {"to": (1, 0)},
            {"to": (2, 0)},
            {"to": (2, 1), "type": "SourceV", "label": {"label": "1V", "loc": "bottom"}},
            {"to": (1, 1), "type": "Resistor", "label": r"10$\Omega$"},
            {"to": (0, 1), "type": "Resistor", "label": r"5$\Omega$"},
            {"from": (0, 0), "to": (0, 1), "type": "SourceV", "label": "$V_S$"},
            {"from": (1, 0), "to": (1, 1), "type": "Resistor", "label": [
                {"label": r"30$\Omega$"},
                {"label": ["-", "$V_R$", "+"], "loc": "bottom"}
            ]},
        ]
    }
    params = data['params'].setdefault('circuit', {})
    params['circuit'] = schematic
