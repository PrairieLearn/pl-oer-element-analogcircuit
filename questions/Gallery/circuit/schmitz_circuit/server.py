def generate(data):
    schematic = {
        "components": [
            {"from": (0, 0), "to": (0, 2), "type": "SourceV", "label": r"$V_1$"},
            {"from": (0, 2), "to": (1, 2), },
            {"from": (0, 0), "to": (1, 0), },
            {"from": (1, 0), "to": (1, 2), "type": "Resistor", "label": r"$R_2$"},
            {"from": (1, 2), "to": (2, 2), },
            {"from": (1, 0), "to": (2, 0), },
            {"from": (2, 0), "to": (2, 1), "type": "Resistor", "label": r"$R_4$"},
            {"from": (2, 1), "to": (2, 2), "type": "Resistor", "label": r"$R_3$"},
        ],
    }
    params = data['params'].setdefault('circuit2', {})
    params['circuit'] = schematic

    schematic = {
        "components": [
            {"from": (0, 0), "to": (1, 0)},
            {"to": (2, 0)},
            {"to": (2, 1), "type": "Resistor"},
            {"to": (3, 1), "type": "Resistor"},
            {"from": (3, 0), "to": (3, 1), "type": "Resistor"},
            {"from": (1, 1), "to": (2, 1), "type": "Resistor"},
            {"from": (1, 2), "to": (2, 2), "type": "Resistor"},
            {"from": (2, 2), "to": (3, 2), "type": "Resistor"},
            {"from": (2, 0), "to": (3, 0)},
            {"from": (1, 1), "to": (0, 1)},
            {"from": (1, 1), "to": (1, 2)},
            {"from": (2, 1), "to": (2, 2)},
            {"from": (3, 1), "to": (3, 2)},
        ],
        "nodes": [
            {"pos": (0, 0), "dot": "open"},
            {"pos": (0, 1), "dot": "open"},
        ]
    }
    params = data['params'].setdefault('circuit3', {})
    params['circuit'] = schematic

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
                {"label": ["+", "$V_R$", "–"], "loc": "bottom"}
            ]},
        ]
    }
    params = data['params'].setdefault('circuit5', {})
    params['circuit'] = schematic

    schematic = {
       "components": [
           { "from": "0,0", "to": "0,4", "type": "SourceV", "label": "$V_S$" },
           { "from": "0,0", "to": "4,0" },
           { "from": "0,4", "to": "3,4", "type": "Resistor", "label": "$R_1$", "annotations": [{"type": "CurrentLabel", "label": "$I_1$", "top": False}]},
           { "from": "2,0", "to": "2,2", "type": "Resistor", "label": "$R_3$"},
           { "from": "2,2", "to": "4,2" },
           { "from": "3,2", "to": "3,4", "type": "Resistor", "label": "$R_2$"},
           { "from": "4,0", "to": "4,2", "type": "SourceI", "label": "$I_S$" },
           { "pos": "2,0", "type": "Ground" }
       ],
       "nodes": [
          { "pos": "0,4", "dot": "filled", "label": "a"},
          { "pos": "3,4", "dot": "filled", "label": "b"},
          { "pos": "3,2", "dot": "filled", "label": "c"}
       ]
    }
    params = data['params'].setdefault('circuit7', {})
    params['circuit'] = schematic

    schematic = {
        "components": [
           { "from": "0,0", "to": "0,1", "type": "SourceV", "label": "$V_1$"},
           { "from": "0,1", "to": "0,2" },
           { "from": "0,0", "to": "1,0" },
           { "from": "0,1", "to": "1,1", "type": "Resistor" },
           { "from": "0,2", "to": "1,2" , "type": "Resistor" },
           { "from": "1,0", "to": "1,1", "type": "Resistor" },
           { "from": "1,1", "to": "1,2" },
           { "from": "1,0", "to": "2,0" },
           { "from": "1,1", "to": "2,1", "type": "Resistor" },
           { "from": "1,2", "to": "2,2", "type": "Resistor" },
           { "from": "2,0", "to": "2,1", "type": "SourceV", "label": "$V_2$" },
           { "from": "2,1", "to": "2,2" },
           { "from": "2,1", "to": "3,1" },
           { "pos": "3,1", "type": "Ground" }
       ],
       "nodes": [
          { "pos": "1,2", "dot": "filled", "label": "$V_b$" }
       ]
    }
    params = data['params'].setdefault('circuit9', {})
    params['circuit'] = schematic