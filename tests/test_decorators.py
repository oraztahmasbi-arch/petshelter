import unittest

from decorators import execution_time, log_operation


class DecoratorTests(unittest.TestCase):
    def test_log_operation_preserves_metadata_and_result(self):
        @log_operation
        def calculate(value):
            """Calculate a simple value."""
            return value + 1

        self.assertEqual(calculate.__name__, "calculate")
        self.assertEqual(calculate.__doc__, "Calculate a simple value.")
        with self.assertLogs("decorators", level="INFO") as captured:
            self.assertEqual(calculate(4), 5)
        output = "\n".join(captured.output)
        self.assertIn("Starting operation", output)
        self.assertIn("Operation completed", output)

    def test_execution_time_logs_even_when_function_fails(self):
        @execution_time
        def fail():
            raise RuntimeError("expected failure")

        with self.assertLogs("decorators", level="INFO") as captured:
            with self.assertRaisesRegex(RuntimeError, "expected failure"):
                fail()
        self.assertIn("executed in", "\n".join(captured.output))

    def test_decorators_do_not_hide_return_values(self):
        @log_operation
        @execution_time
        def greet(name):
            return f"Hello {name}"

        with self.assertLogs("decorators", level="INFO"):
            self.assertEqual(greet("Pet Shelter"), "Hello Pet Shelter")


if __name__ == "__main__":
    unittest.main()
