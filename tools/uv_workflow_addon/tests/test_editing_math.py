import unittest
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import editing_math


def _uv_from_pixels(points, width, height):
    points = np.asarray(points, dtype=np.float64)
    dimensions = np.asarray((width, height), dtype=np.float64)
    return (points / dimensions).astype(np.float32)


class EditingMathTests(unittest.TestCase):
    def test_rotate_90_uses_1024x512_pixel_space_and_nonzero_pivot(self):
        width, height = 1024, 512
        uv = np.array([
            [0.12345679, 0.87654322],
            [350 / 1024, 50 / 512],
            [0.33333334, 0.70000000],
            [356 / 1024, 50 / 512],
            [356 / 1024, 178 / 512],
            [0.90000000, 0.11111112],
        ], dtype=np.float32)
        original = uv.copy()
        original_bytes = uv.tobytes()
        indices = [1, 3, 4]

        new_uv, details = editing_math.apply_coordinates(
            uv,
            indices,
            {
                "kind": "rotate",
                "angle_degrees": 90,
                "pivot_px": [300, 100],
            },
            width,
            height,
        )

        expected = uv.copy()
        expected[indices] = _uv_from_pixels(
            [(350, 150), (350, 156), (222, 156)], width, height)
        np.testing.assert_array_equal(new_uv, expected)
        np.testing.assert_array_equal(new_uv[[0, 2, 5]], uv[[0, 2, 5]])
        self.assertEqual(uv.tobytes(), original_bytes)
        np.testing.assert_array_equal(uv, original)
        self.assertEqual(new_uv.dtype, np.float32)
        self.assertEqual(new_uv.shape, uv.shape)
        self.assertFalse(np.shares_memory(new_uv, uv))
        self.assertEqual(details["kind"], "rotate")
        self.assertEqual(details["selected_count"], 3)
        self.assertEqual(details["changed_count"], 3)
        self.assertEqual(details["pivot_px"], [300.0, 100.0])
        self.assertNotIn("uv", details)

    def test_rotate_90_uses_exact_discrete_cosine_and_sine(self):
        # A trig-computed cos(pi/2) would move x by about 6,000 pixels here.
        uv = np.array([[1e20, 0.0]], dtype=np.float32)
        expected = np.array([[0.0, uv[0, 0]]], dtype=np.float32)

        for angle in (90.0, 450.0, -270.0):
            with self.subTest(angle=angle):
                new_uv, details = editing_math.apply_coordinates(
                    uv,
                    [0],
                    {
                        "kind": "rotate",
                        "angle_degrees": angle,
                        "pivot_px": [0, 0],
                    },
                    1,
                    1,
                )
                np.testing.assert_array_equal(new_uv, expected)
                self.assertEqual(details["changed_count"], 1)
                self.assertEqual(details["pivot_px"], [0.0, 0.0])

    def test_identity_actions_and_full_turns_are_byte_exact_noops(self):
        uv = np.array([
            [0.12345679, 0.87654322],
            [0.00010000, 0.99990000],
            [0.50000000, 0.50000000],
            [0.33333334, 0.70000000],
        ], dtype=np.float32)
        original_bytes = uv.tobytes()
        indices = [0, 2, 3]
        actions = (
            ("zero translate", {
                "kind": "translate", "delta_px": [0.0, -0.0]}),
            ("zero rotation", {
                "kind": "rotate", "angle_degrees": 0.0,
                "pivot_px": [123.456, 234.567]}),
            ("full turn default pivot", {
                "kind": "rotate", "angle_degrees": 360.0}),
            ("negative multiple turn", {
                "kind": "rotate", "angle_degrees": -720.0}),
            ("unit scale", {
                "kind": "scale", "factors": [1.0, 1.0]}),
            ("unit scale explicit pivot", {
                "kind": "scale", "factors": [1.0, 1.0],
                "pivot_px": [12.3, 45.6]}),
        )

        for label, action in actions:
            with self.subTest(action=label):
                new_uv, details = editing_math.apply_coordinates(
                    uv, indices, action, 1023, 511)
                self.assertEqual(new_uv.tobytes(), original_bytes)
                self.assertEqual(uv.tobytes(), original_bytes)
                self.assertFalse(np.shares_memory(new_uv, uv))
                self.assertEqual(details["selected_count"], 3)
                self.assertEqual(details["changed_count"], 0)

    def test_translate_uses_pixels_and_preserves_unselected_values(self):
        width, height = 1024, 512
        uv = np.array([
            [0.12345679, 0.87654322],
            [100 / 1024, 50 / 512],
            [0.33333334, 0.70000000],
            [900 / 1024, 400 / 512],
        ], dtype=np.float32)
        original = uv.copy()
        indices = [1, 3]

        new_uv, details = editing_math.apply_coordinates(
            uv,
            indices,
            {"kind": "translate", "delta_px": [512, -128]},
            width,
            height,
        )

        expected = uv.copy()
        expected[indices] = _uv_from_pixels(
            [(612, -78), (1412, 272)], width, height)
        np.testing.assert_array_equal(new_uv, expected)
        np.testing.assert_array_equal(new_uv[[0, 2]], uv[[0, 2]])
        np.testing.assert_array_equal(uv, original)
        self.assertEqual(details["kind"], "translate")
        self.assertEqual(details["selected_count"], 2)
        self.assertEqual(details["changed_count"], 2)
        self.assertNotIn("pivot_px", details)

    def test_scale_uses_default_pixel_bbox_pivot(self):
        width, height = 1024, 512
        uv = np.array([
            [0.12345679, 0.87654322],
            [100 / 1024, 100 / 512],
            [0.33333334, 0.70000000],
            [300 / 1024, 300 / 512],
        ], dtype=np.float32)
        original = uv.copy()
        indices = [1, 3]

        new_uv, details = editing_math.apply_coordinates(
            uv,
            indices,
            {"kind": "scale", "factors": [2.0, 0.5]},
            width,
            height,
        )

        expected = uv.copy()
        expected[indices] = _uv_from_pixels(
            [(0, 150), (400, 250)], width, height)
        np.testing.assert_array_equal(new_uv, expected)
        np.testing.assert_array_equal(new_uv[[0, 2]], uv[[0, 2]])
        np.testing.assert_array_equal(uv, original)
        self.assertEqual(details["kind"], "scale")
        self.assertEqual(details["selected_count"], 2)
        self.assertEqual(details["changed_count"], 2)
        self.assertEqual(details["pivot_px"], [200.0, 200.0])

    def test_mirror_flips_only_the_requested_axis(self):
        width, height = 1024, 512
        uv = np.array([
            [0.12345679, 0.87654322],
            [100 / 1024, 100 / 512],
            [0.33333334, 0.70000000],
            [300 / 1024, 300 / 512],
        ], dtype=np.float32)
        original = uv.copy()
        indices = [1, 3]

        new_uv, details = editing_math.apply_coordinates(
            uv,
            indices,
            {"kind": "mirror", "axis": "U"},
            width,
            height,
        )

        expected = uv.copy()
        expected[indices] = _uv_from_pixels(
            [(300, 100), (100, 300)], width, height)
        np.testing.assert_array_equal(new_uv, expected)
        np.testing.assert_array_equal(new_uv[:, 1], uv[:, 1])
        np.testing.assert_array_equal(new_uv[[0, 2]], uv[[0, 2]])
        np.testing.assert_array_equal(uv, original)
        self.assertEqual(details["kind"], "mirror")
        self.assertEqual(details["selected_count"], 2)
        self.assertEqual(details["changed_count"], 2)
        self.assertEqual(details["pivot_px"], [200.0, 200.0])

    def test_align_defaults_to_axis_mean_and_preserves_other_axis(self):
        width, height = 1024, 512
        uv = np.array([
            [0.12345679, 0.87654322],
            [100 / 1024, 50 / 512],
            [300 / 1024, 100 / 512],
            [0.90000000, 0.80000000],
            [500 / 1024, 150 / 512],
        ], dtype=np.float32)
        original = uv.copy()
        indices = [1, 2, 4]

        new_uv, details = editing_math.apply_coordinates(
            uv,
            indices,
            {"kind": "align", "axis": "U"},
            width,
            height,
        )

        expected = uv.copy()
        expected[indices, 0] = np.float32(300 / 1024)
        np.testing.assert_array_equal(new_uv, expected)
        np.testing.assert_array_equal(new_uv[:, 1], uv[:, 1])
        np.testing.assert_array_equal(new_uv[[0, 3]], uv[[0, 3]])
        np.testing.assert_array_equal(uv, original)
        self.assertEqual(details["kind"], "align")
        self.assertEqual(details["selected_count"], 3)
        self.assertEqual(details["changed_count"], 2)
        self.assertNotIn("pivot_px", details)

    def test_align_explicit_value_changes_only_requested_axis(self):
        width, height = 1024, 512
        uv = np.array([
            [0.12345679, 0.87654322],
            [100 / 1024, 50 / 512],
            [300 / 1024, 100 / 512],
            [0.90000000, 0.80000000],
            [500 / 1024, 150 / 512],
        ], dtype=np.float32)
        original = uv.copy()
        indices = [1, 2, 4]

        new_uv, details = editing_math.apply_coordinates(
            uv,
            indices,
            {"kind": "align", "axis": "V", "value_px": 64.0},
            width,
            height,
        )

        expected = uv.copy()
        expected[indices, 1] = np.float32(64 / 512)
        np.testing.assert_array_equal(new_uv, expected)
        np.testing.assert_array_equal(new_uv[:, 0], uv[:, 0])
        np.testing.assert_array_equal(new_uv[[0, 3]], uv[[0, 3]])
        np.testing.assert_array_equal(uv, original)
        self.assertEqual(details["selected_count"], 3)
        self.assertEqual(details["changed_count"], 3)

    def test_straighten_uses_ordered_cumulative_arc_length(self):
        width, height = 1024, 512
        uv = np.array([
            [0.11111112, 0.22222224],
            [0.33333334, 0.44444448],
            [200 / 1024, 100 / 512],
            [0.77777779, 0.88888890],
            [100 / 1024, 100 / 512],
            [200 / 1024, 300 / 512],
        ], dtype=np.float32)
        original = uv.copy()
        indices = [4, 2, 5]

        new_uv, details = editing_math.apply_coordinates(
            uv,
            indices,
            {"kind": "straighten"},
            width,
            height,
        )

        expected = uv.copy()
        expected[2] = _uv_from_pixels(
            [[100 + 100 / 3, 100 + 200 / 3]], width, height)[0]
        np.testing.assert_array_equal(new_uv, expected)
        self.assertEqual(new_uv[4].tobytes(), uv[4].tobytes())
        self.assertEqual(new_uv[5].tobytes(), uv[5].tobytes())
        np.testing.assert_array_equal(new_uv[[0, 1, 3]], uv[[0, 1, 3]])
        np.testing.assert_array_equal(uv, original)
        self.assertEqual(details["kind"], "straighten")
        self.assertEqual(details["selected_count"], 3)
        self.assertEqual(details["changed_count"], 1)
        self.assertNotIn("pivot_px", details)

    def test_invalid_uv_and_indices_raise_value_error(self):
        uv = np.array([
            [0.1, 0.2],
            [0.3, 0.4],
            [0.5, 0.6],
            [0.7, 0.8],
        ], dtype=np.float32)
        action = {"kind": "translate", "delta_px": [1, 2]}
        bad_uvs = (
            ("one dimensional", np.zeros(2, dtype=np.float32)),
            ("three columns", np.zeros((2, 3), dtype=np.float32)),
            ("nan", np.array([[0.1, np.nan]], dtype=np.float32)),
            ("infinity", np.array([[np.inf, 0.2]], dtype=np.float32)),
            ("object dtype", np.array([["0", "1"]], dtype=object)),
            ("ragged", [[0.1, 0.2], [0.3]]),
            ("float64 overflow", np.array([[1e40, 0.0]], dtype=np.float64)),
        )
        for label, value in bad_uvs:
            with self.subTest(kind="uv", case=label):
                with self.assertRaises(ValueError):
                    editing_math.apply_coordinates(
                        value, [0], action, 1024, 512)

        bad_indices = (
            ("empty", []),
            ("duplicate", [0, 0]),
            ("out of range", [0, 99]),
            ("negative", [-1]),
            ("bool", [True]),
            ("float", [0.0]),
            ("string", ["0"]),
            ("nested", [[0, 1]]),
            ("two dimensional", np.array([[0, 1]], dtype=np.int64)),
            ("none", None),
        )
        for label, value in bad_indices:
            with self.subTest(kind="indices", case=label):
                with self.assertRaises(ValueError):
                    editing_math.apply_coordinates(
                        uv, value, action, 1024, 512)

    def test_invalid_dimensions_raise_value_error(self):
        uv = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
        action = {"kind": "translate", "delta_px": [1, 2]}
        cases = (
            ("zero width", 0, 512),
            ("zero height", 1024, 0),
            ("negative width", -1, 512),
            ("negative height", 1024, -512),
            ("float width", 1024.0, 512),
            ("float height", 1024, 512.0),
            ("bool width", True, 512),
            ("bool height", 1024, False),
        )
        for label, width, height in cases:
            with self.subTest(case=label):
                with self.assertRaises(ValueError):
                    editing_math.apply_coordinates(
                        uv, [0], action, width, height)

    def test_invalid_actions_raise_value_error(self):
        uv = np.array([
            [0.1, 0.2],
            [0.3, 0.4],
            [0.5, 0.6],
            [0.7, 0.8],
        ], dtype=np.float32)
        indices = [0, 2]
        actions = (
            ("not mapping", None),
            ("list", []),
            ("missing kind", {}),
            ("unknown kind", {"kind": "bogus"}),
            ("missing delta", {"kind": "translate"}),
            ("translate unknown field", {
                "kind": "translate", "delta_px": [0, 0], "extra": 1}),
            ("nan delta", {
                "kind": "translate", "delta_px": [np.nan, 0]}),
            ("short delta", {
                "kind": "translate", "delta_px": [0]}),
            ("bool delta", {
                "kind": "translate", "delta_px": [True, False]}),
            ("infinite angle", {
                "kind": "rotate", "angle_degrees": np.inf}),
            ("short pivot", {
                "kind": "rotate", "angle_degrees": 90, "pivot_px": [0]}),
            ("nan pivot", {
                "kind": "rotate", "angle_degrees": 90,
                "pivot_px": [0, np.nan]}),
            ("zero scale", {
                "kind": "scale", "factors": [0.0, 1.0]}),
            ("negative scale", {
                "kind": "scale", "factors": [-1.0, 1.0]}),
            ("infinite scale", {
                "kind": "scale", "factors": [1.0, np.inf]}),
            ("short factors", {
                "kind": "scale", "factors": [1.0]}),
            ("bad mirror axis", {
                "kind": "mirror", "axis": "X"}),
            ("mirror unknown field", {
                "kind": "mirror", "axis": "U",
                "pivot_px": [0, 0], "extra": 0}),
            ("lowercase axis", {
                "kind": "align", "axis": "u"}),
            ("nan align value", {
                "kind": "align", "axis": "V", "value_px": np.nan}),
            ("bool align value", {
                "kind": "align", "axis": "V", "value_px": True}),
            ("align pivot", {
                "kind": "align", "axis": "U", "pivot_px": [0, 0]}),
            ("straighten unknown field", {
                "kind": "straighten", "unexpected": 1}),
        )
        for label, action in actions:
            with self.subTest(case=label):
                with self.assertRaises(ValueError):
                    editing_math.apply_coordinates(
                        uv, indices, action, 1024, 512)

    def test_straighten_rejects_too_few_or_coincident_endpoints(self):
        uv = np.array([
            [0.1, 0.1],
            [0.2, 0.2],
            [0.3, 0.3],
        ], dtype=np.float32)
        cases = (
            ("two points", uv[:2], [0, 1]),
            ("same endpoints", uv, [0, 1, 0]),
            ("all points coincide", np.repeat(
                np.array([[0.1, 0.1]], dtype=np.float32), 3, axis=0),
             [0, 1, 2]),
        )
        for label, values, indices in cases:
            with self.subTest(case=label):
                with self.assertRaises(ValueError):
                    editing_math.apply_coordinates(
                        values, indices, {"kind": "straighten"}, 1024, 512)

    def test_float32_output_overflow_is_rejected_without_input_mutation(self):
        uv = np.array([[1.0, 0.5], [0.25, 0.75]], dtype=np.float32)
        original = uv.copy()
        cases = (
            ("scale", {
                "kind": "scale", "factors": [1e39, 1.0],
                "pivot_px": [0.0, 0.0]}),
            ("translate", {
                "kind": "translate", "delta_px": [1e308, 0.0]}),
            ("align", {
                "kind": "align", "axis": "U", "value_px": 1e308}),
        )
        for label, action in cases:
            with self.subTest(action=label):
                with self.assertRaises(ValueError):
                    editing_math.apply_coordinates(
                        uv, [0], action, 1024, 512)
                np.testing.assert_array_equal(uv, original)


if __name__ == "__main__":
    unittest.main()
