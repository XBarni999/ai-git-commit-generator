import os
import sys
import unittest

# Ensure the root directory is in the path so we can import main and config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main


class TestCommitGenerator(unittest.TestCase):

    def test_clean_commit_message_simple(self):
        msg = "feat: add user login endpoint"
        cleaned = main.clean_commit_message(msg)
        self.assertEqual(cleaned, "feat: add user login endpoint")

    def test_clean_commit_message_with_extra_prefix(self):
        msg = 'Commit message: "fix: resolve memory leak in parser"'
        cleaned = main.clean_commit_message(msg)
        self.assertEqual(cleaned, "fix: resolve memory leak in parser")

    def test_clean_commit_message_multiline_body(self):
        msg = (
            "Here is the message:\n\n"
            "feat: add database migration\n\n"
            "- Add migration script for users table\n"
            "- Update schema definition"
        )
        cleaned = main.clean_commit_message(msg)
        expected = (
            "feat: add database migration\n\n"
            "- Add migration script for users table\n"
            "- Update schema definition"
        )
        self.assertEqual(cleaned, expected)

    def test_is_conventional_commit_valid(self):
        self.assertTrue(main.is_conventional_commit("feat: add something"))
        self.assertTrue(main.is_conventional_commit("fix(auth): correct password check"))
        self.assertTrue(main.is_conventional_commit("chore: update readme"))
        self.assertTrue(main.is_conventional_commit("docs(api): document endpoints"))
        self.assertTrue(main.is_conventional_commit("refactor: clean up loop"))

    def test_is_conventional_commit_invalid(self):
        self.assertFalse(main.is_conventional_commit("added new features"))
        self.assertFalse(main.is_conventional_commit("feat add something"))
        self.assertFalse(main.is_conventional_commit("random text: not conventional"))

    def test_check_50_72_compliance_good(self):
        # 43 chars subject
        msg = "feat: add user login endpoint"
        warnings = main.check_50_72_compliance(msg)
        self.assertEqual(warnings, [])

    def test_check_50_72_compliance_good_multiline(self):
        msg = (
            "feat: add user login endpoint\n"
            "\n"
            "This is a body line that is well under seventy-two characters."
        )
        warnings = main.check_50_72_compliance(msg)
        self.assertEqual(warnings, [])

    def test_check_50_72_compliance_long_subject(self):
        # 55 chars subject
        msg = "feat: add user login endpoint with OAuth2 and password recovery"
        warnings = main.check_50_72_compliance(msg)
        self.assertTrue(any("Subject line exceeds 50 characters" in w for w in warnings))

    def test_check_50_72_compliance_missing_blank_line(self):
        msg = (
            "feat: add user login endpoint\n"
            "This body is missing the blank line separator."
        )
        warnings = main.check_50_72_compliance(msg)
        self.assertTrue(any("separated by a blank line" in w for w in warnings))

    def test_check_50_72_compliance_long_body_line(self):
        msg = (
            "feat: add user login\n"
            "\n"
            "This body line is extremely long, definitely exceeding the seventy-two character limit that we want to enforce in our conventional commits standards."
        )
        warnings = main.check_50_72_compliance(msg)
        self.assertTrue(any("exceeds 72 characters" in w for w in warnings))


if __name__ == "__main__":
    unittest.main()
