import random


def generate(data):
    data["params"]["readme_circuit"] = {
        "circuit": {
            "components": [
                {"from": "0,0", "to": "0,3", "type": "SourceV", "label": "$V_S$"},
                {"from": "0,3", "to": "4,3", "type": "Resistor", "label": "$R_1$"},
                {"from": "4,3", "to": "4,0", "type": "Resistor", "label": "$R_2$"},
                {"from": "4,0", "to": "0,0"},
                {"pos": "0,0", "type": "Ground"},
            ],
            "nodes": [
                {"pos": "0,3", "dot": "filled", "label": "a"},
            ],
            "annotations": [
                {"type": "LoopCurrent", "bounds": ["0,0", "4,3"], "label": "$I$"},
            ],
        }
    }

    source_voltage = random.choice([6, 9, 12, 15])
    r1 = random.choice([1000, 1500, 2200, 3300, 4700])
    r2 = random.choice([1000, 1500, 2200, 3300, 4700])
    vout = source_voltage * r2 / (r1 + r2)

    data["params"]["random_circuit"] = {
        "circuit": {
            "components": [
                {
                    "from": "0,0",
                    "to": "0,3",
                    "type": "SourceV",
                    "label": f"${source_voltage}\\,V$",
                },
                {
                    "from": "0,3",
                    "to": "3,3",
                    "type": "Resistor",
                    "label": f"$R_1={r1 / 1000:g}\\,k\\Omega$",
                },
                {
                    "from": "3,3",
                    "to": "3,0",
                    "type": "Resistor",
                    "label": [
                        f"$R_2={r2 / 1000:g}\\,k\\Omega$",
                        {"label": ["+", "$V_{out}$", "-"], "loc": "bottom"},
                    ],
                },
                {"from": "3,0", "to": "0,0"},
                {"pos": "0,0", "type": "Ground"},
            ],
            "nodes": [
                {"pos": "3,3", "dot": "filled", "label": "out"},
            ],
            "annotations": [
                {"type": "LoopCurrent", "bounds": ["0,0", "3,3"], "label": "$I$"},
            ],
        }
    }

    data["correct_answers"]["vout"] = vout
