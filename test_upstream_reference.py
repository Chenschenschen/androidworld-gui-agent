"""Check the reference boundary independently of API/emulator availability."""

import unittest
from upstream_reference import check_action, literal_call


class ReferenceBoundaryTests(unittest.TestCase):
    """Protect the model-code boundary while leaving upstream policy unchanged."""

    def test_literals_only(self):
        """Nested calls and metadata overrides cannot pass to execution."""
        for text in ('do(action="Type", text=open("secret").read())',
                     'do(action="Home", _metadata="finish")',
                     'do(action="Home"); do(action="Home")'):
            with self.assertRaises((ValueError, SyntaxError)):
                literal_call(text)

    def test_bounds(self):
        """Reject invalid coordinates and unbounded wait operations."""
        for text in ('do(action="Tap", element=[1001,20])',
                     'do(action="Wait", duration="900 seconds")',
                     'do(action="Take_over", message="login")'):
            with self.assertRaises(ValueError):
                check_action(literal_call(text))

    def test_valid_native_actions(self):
        """Native valid calls retain literal values through the checked boundary."""
        for text in ('do(action="Tap", element=[500,250])',
                     'do(action="Type", text="john.doe@example.com")',
                     'finish(message="Completed")'):
            check_action(literal_call(text))


if __name__ == "__main__":
    unittest.main()
