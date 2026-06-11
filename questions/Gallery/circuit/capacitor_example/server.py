def generate(data):
    schematic = {
        "components": [
            {"from": (0, 0), "to": (1, 0), "type": "Capacitor", "label": "40nF"},
            {"from": (1, 0), "to": (2, 0), "type": "Capacitor", "label": "32nF"},
            {"from": (1, 0), "to": (1, 1), "type": "Capacitor", "label": "2.8nF"},
            {"from": (2, 0), "to": (2, 1), "type": "Capacitor", "label": "8nF"},
            {"from": (1, 0), "to": (2, 1), "type": "Capacitor", "label": "5.6nF"},
            {"from": (1, 1), "to": (2, 1), "type": "Capacitor", "label": "18nF"},
            {"from": (0, 1), "to": (1, 1), "type": "Capacitor", "label": "8nF"},
        ],
        "nodes": [
            {"pos": (0, 0), "dot": "filled", "label": "b"},
            {"pos": (0, 1), "dot": "filled", "label": "a"},
        ]
    }
    params = data['params'].setdefault('circuit', {})
    params['circuit'] = schematic

    data["correct_answers"]["value"] = 0
