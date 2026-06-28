import sys
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from circuit.formats.circuitikz import from_circuitikz  # noqa: E402


class CircuitikzParserTests(unittest.TestCase):
    def test_basic_loop_components_and_labels(self) -> None:
        raw = r"""
        \begin{circuitikz}[american voltages]
        \draw (0,0) to[R=$R_1$,-*] (2,0) to[sV, v^>={$V_{in}$}, -*] (2,2) -- (0,2) -- (0,0);
        \end{circuitikz}
        """
        circuit = from_circuitikz(raw)
        components = circuit["components"]

        self.assertEqual(len(components), 4)
        self.assertEqual(components[0].get("type"), "ResistorIEEE")
        self.assertEqual(components[0].get("label"), "$R_1$")

        self.assertEqual(components[1].get("type"), "SourceV")
        self.assertEqual(components[1].get("label"), "$V_{in}$")

        self.assertEqual(components[2].get("type"), "Line")
        self.assertEqual(components[3].get("type"), "Line")

        node_map = {tuple(node["pos"]): node for node in circuit.get("nodes", [])}
        self.assertEqual(node_map[(2, 0)].get("dot"), "filled")
        self.assertEqual(node_map[(2, 2)].get("dot"), "filled")

    def test_relative_coordinates_and_double_dots(self) -> None:
        raw = r"""
        \begin{circuitikz}
        \draw (0,0) to[R,l={$R_{load}$},*-*] ++(2,0);
        \end{circuitikz}
        """
        circuit = from_circuitikz(raw)
        components = circuit["components"]

        self.assertEqual(len(components), 1)
        resistor = components[0]
        self.assertEqual(resistor.get("type"), "ResistorIEC")
        self.assertEqual(resistor.get("from"), (0, 0))
        self.assertEqual(resistor.get("to"), (2, 0))
        self.assertEqual(resistor.get("label"), {"label": "$R_{load}$", "loc": "top"})

        node_map = {tuple(node["pos"]): node for node in circuit.get("nodes", [])}
        self.assertEqual(node_map[(0, 0)].get("dot"), "filled")
        self.assertEqual(node_map[(2, 0)].get("dot"), "filled")

    def test_tikzpicture_battery_and_resistor_loop(self) -> None:
        raw = r"""
        \begin{tikzpicture}
            \draw (7, 5) to[battery] (7, 7);
            \draw (7, 7) to[american resistor] (10, 7);
            \draw (10, 7) -- (10, 5) -- (7, 5);
        \end{tikzpicture}
        """
        circuit = from_circuitikz(raw)
        components = circuit["components"]

        self.assertEqual(len(components), 4)

        self.assertEqual(components[0].get("type"), "Battery")
        self.assertEqual(components[0].get("from"), (7, 5))
        self.assertEqual(components[0].get("to"), (7, 7))

        self.assertEqual(components[1].get("type"), "ResistorIEEE")
        self.assertEqual(components[1].get("from"), (7, 7))
        self.assertEqual(components[1].get("to"), (10, 7))

        self.assertEqual(components[2].get("type"), "Line")
        self.assertEqual(components[2].get("from"), (10, 7))
        self.assertEqual(components[2].get("to"), (10, 5))

        self.assertEqual(components[3].get("type"), "Line")
        self.assertEqual(components[3].get("from"), (10, 5))
        self.assertEqual(components[3].get("to"), (7, 5))

        self.assertFalse(circuit.get("nodes"))

    def test_ground_node_generates_single_component(self) -> None:
        raw = r"""
        \begin{circuitikz}
        \draw (0,0) -- (2,0) node[ground] {};
        \end{circuitikz}
        """
        circuit = from_circuitikz(raw)
        components = circuit["components"]

        self.assertEqual(len(components), 2)
        self.assertEqual(components[0].get("type"), "Line")
        ground = components[1]
        self.assertEqual(ground.get("type"), "Ground")
        self.assertEqual(ground.get("pos"), (2, 0))

    def test_american_modifier_on_resistor_token(self) -> None:
        raw = r"""
        \begin{circuitikz}
        \draw (0,0) to[american resistor] (2,0);
        \end{circuitikz}
        """
        circuit = from_circuitikz(raw)
        components = circuit["components"]

        self.assertEqual(len(components), 1)
        self.assertEqual(components[0].get("type"), "ResistorIEEE")

    def test_american_voltage_source_with_parallel_resistors(self) -> None:
        raw = r"""
        \begin{tikzpicture}
            \draw (5, 5) to[american voltage source, v^>={12V}] (5, 2);
            \draw (5, 5) to[american resistor, R={4k}] (8, 5);
            \draw (11, 5) -- (11, 2);
            \draw (8, 5) to[american resistor, R={6k}] (11, 5);
            \draw (8, 5) to[american resistor, R={8k}] (8, 2);
            \draw (5, 2) -- (8, 2);
            \draw (8, 2) -- (11, 2);
        \end{tikzpicture}
        """
        circuit = from_circuitikz(raw)
        components = circuit["components"]

        self.assertEqual(len(components), 7)

        self.assertEqual(components[0].get("type"), "SourceV")
        self.assertEqual(components[0].get("from"), (5, 5))
        self.assertEqual(components[0].get("to"), (5, 2))
        self.assertEqual(components[0].get("label"), "12V")

        self.assertEqual(components[1].get("type"), "ResistorIEEE")
        self.assertEqual(components[1].get("from"), (5, 5))
        self.assertEqual(components[1].get("to"), (8, 5))
        self.assertEqual(components[1].get("label"), "4k")

        self.assertEqual(components[2].get("type"), "Line")
        self.assertEqual(components[2].get("from"), (11, 5))
        self.assertEqual(components[2].get("to"), (11, 2))

        self.assertEqual(components[3].get("type"), "ResistorIEEE")
        self.assertEqual(components[3].get("from"), (8, 5))
        self.assertEqual(components[3].get("to"), (11, 5))
        self.assertEqual(components[3].get("label"), "6k")

        self.assertEqual(components[4].get("type"), "ResistorIEEE")
        self.assertEqual(components[4].get("from"), (8, 5))
        self.assertEqual(components[4].get("to"), (8, 2))
        self.assertEqual(components[4].get("label"), "8k")

        self.assertEqual(components[5].get("type"), "Line")
        self.assertEqual(components[5].get("from"), (5, 2))
        self.assertEqual(components[5].get("to"), (8, 2))

        self.assertEqual(components[6].get("type"), "Line")
        self.assertEqual(components[6].get("from"), (8, 2))
        self.assertEqual(components[6].get("to"), (11, 2))

    def test_short_with_label_and_annotation_positions(self) -> None:
        raw = r"""
        \begin{circuitikz}
        \draw (0,0) to[short,l^={$I$},a_={node}] (2,0);
        \end{circuitikz}
        """
        circuit = from_circuitikz(raw)
        component = circuit["components"][0]

        self.assertEqual(component.get("type"), "Line")
        self.assertEqual(component.get("from"), (0, 0))
        self.assertEqual(component.get("to"), (2, 0))

        labels = component.get("label")
        self.assertIsInstance(labels, list)
        self.assertEqual(
            labels, [{"label": "$I$", "loc": "top"}, {"label": "node", "loc": "bottom"}]
        )


if __name__ == "__main__":
    unittest.main()
