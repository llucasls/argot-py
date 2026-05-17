import unittest


class TestCase(unittest.TestCase):
    def assertDictEqual(self, actual, expected, msg = None):
        """
        Assert the output dict has the same key/value pairs
        as the expected one.
        """
        unexpected = {}
        not_found = {}
        different = {}

        for key, expected_value in expected.items():
            if key not in actual:
                not_found[key] = expected_value
                continue

            actual_value = actual[key]

            if actual_value != expected_value:
                different[key] = (actual_value, expected_value)

        for key, actual_value in actual.items():
            if key not in expected:
                unexpected[key] = actual_value

        if unexpected or not_found or different:
            parts = ["dictionaries did not match:"]

            if msg is not None:
                parts[0] = f"dictionaries did not match: {msg}"

            if unexpected:
                parts.append(f"    unexpected: {unexpected}")

            if not_found:
                parts.append(f"    not found: {not_found}")

            if different:
                parts.append(f"    different: {different}")

            raise AssertionError("\n".join(parts))

    def assertDictMatch(self, actual, expected, msg = None):
        """
        Assert the output dict has all key/value pairs present in
        the expected dict. The observed dictionary may have extra
        pairs not present in the expected dictionary.
        """
        not_found = {}
        different = {}

        for key, expected_value in expected.items():
            if key not in actual:
                not_found[key] = expected_value
                continue

            actual_value = actual[key]

            if actual_value != expected_value:
                different[key] = (actual_value, expected_value)

        if not_found or different:
            parts = ["dictionaries did not match:"]

            if msg is not None:
                parts[0] = f"dictionaries did not match: {msg}"

            if not_found:
                parts.append(f"    not found: {not_found}")

            if different:
                parts.append(f"    different: {different}")

            raise AssertionError("\n".join(parts))
