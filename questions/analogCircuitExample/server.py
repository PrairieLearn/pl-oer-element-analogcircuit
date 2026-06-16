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
    left_resistor = random.choice([1000, 1500, 2200, 3300, 4700])
    right_resistor = random.choice([1000, 1500, 2200, 3300, 4700])
    source_current_ma = 1000 * (
        source_voltage / left_resistor + source_voltage / right_resistor
    )

    data["params"]["random_circuit"] = {
        "circuit": {
            "components": [
                {
                    "from": "3,0",
                    "to": "3,3",
                    "type": "SourceV",
                    "label": f"${source_voltage}\\,V$",
                },
                {"from": "3,3", "to": "0,3"},
                {
                    "from": "0,3",
                    "to": "0,0",
                    "type": "Resistor",
                    "label": f"$R_L={left_resistor / 1000:g}\\,k\\Omega$",
                },
                {"from": "0,0", "to": "3,0"},
                {"from": "3,3", "to": "6,3"},
                {
                    "from": "6,3",
                    "to": "6,0",
                    "type": "Resistor",
                    "label": f"$R_R={right_resistor / 1000:g}\\,k\\Omega$",
                },
                {"from": "6,0", "to": "3,0"},
                {"pos": "3,0", "type": "Ground"},
            ],
            "nodes": [
                {"pos": "3,3", "dot": "filled"},
                {"pos": "3,0", "dot": "filled"},
            ],
            "annotations": [
                {"type": "LoopCurrent", "bounds": ["0,0", "3,3"], "label": "$I_L$"},
                {"type": "LoopCurrent", "bounds": ["3,0", "6,3"], "label": "$I_R$"},
            ],
        }
    }

    data["correct_answers"]["source_current"] = source_current_ma
