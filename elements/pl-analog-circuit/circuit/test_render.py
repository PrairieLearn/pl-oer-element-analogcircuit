import sys
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from circuit.render import orient_labels  # noqa: E402


class RenderTests(unittest.TestCase):
    def test_side_right_maps_to_centered_vertical_label_loc(self) -> None:
        labels = orient_labels((2, 3), (2, 0), [{"label": "$R$", "side": "right"}])

        self.assertEqual(labels, [{"label": "$R$", "loc": "bottom"}])

    def test_existing_loc_takes_precedence_over_side(self) -> None:
        labels = orient_labels(
            (2, 3),
            (2, 0),
            [{"label": "$R$", "side": "right", "loc": "top"}],
        )

        self.assertEqual(labels, [{"label": "$R$", "loc": "top"}])


if __name__ == "__main__":
    unittest.main()
