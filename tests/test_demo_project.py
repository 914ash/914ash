import unittest

from demo_project.service import evaluate_payload


class DemoProjectTests(unittest.TestCase):
    def test_evaluate_payload_success(self) -> None:
        result = evaluate_payload(
            {"name": "demo", "priority": 2, "completed": True}
        )
        self.assertEqual(result["points"], 20)
        self.assertEqual(result["status"], "done")

    def test_missing_required_field_is_loud(self) -> None:
        with self.assertRaisesRegex(ValueError, "Missing required fields: completed"):
            evaluate_payload({"name": "demo", "priority": 2})

    def test_priority_boundary_validation(self) -> None:
        with self.assertRaisesRegex(ValueError, "priority"):
            evaluate_payload(
                {"name": "demo", "priority": 99, "completed": False}
            )


if __name__ == "__main__":
    unittest.main()
