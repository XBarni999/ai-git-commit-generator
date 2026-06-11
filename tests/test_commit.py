import os
import sys
import unittest

# Ensure the root directory is in the path so we can import main and config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main
import config
import unittest.mock


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



class TestConfigKeys(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.temp_config = tempfile.mktemp(suffix=".json")
        self.old_config_file = config.CONFIG_FILE
        config.CONFIG_FILE = self.temp_config

    def tearDown(self):
        import os
        if os.path.exists(self.temp_config):
            try:
                os.remove(self.temp_config)
            except Exception:
                pass
        config.CONFIG_FILE = self.old_config_file

    def test_save_and_load_groq_key(self):
        import config
        config.set_groq_api_key("gsk_test_12345")
        cfg = config.load_config()
        self.assertEqual(cfg.get("groq_api_key"), "gsk_test_12345")

    def test_save_and_load_openrouter_key(self):
        import config
        config.set_openrouter_api_key("sk-or-test-67890")
        cfg = config.load_config()
        self.assertEqual(cfg.get("openrouter_api_key"), "sk-or-test-67890")

    def test_clear_groq_key(self):
        import config
        config.set_groq_api_key("gsk_test_12345")
        config.set_groq_api_key("")
        cfg = config.load_config()
        self.assertEqual(cfg.get("groq_api_key"), "")


class TestPremiumFeatures(unittest.TestCase):
    @unittest.mock.patch("main.generate_ai_response")
    @unittest.mock.patch("config.is_pro_active")
    def test_diff_truncation_free(self, mock_is_pro, mock_ai_response):
        mock_is_pro.return_value = False
        mock_ai_response.return_value = "feat: add dummy commit"
        
        long_diff = "a" * 3000
        main.generate_commit_message(long_diff, "model", "url", 90)
        
        # Check that the diff passed to generate_ai_response was truncated
        args, kwargs = mock_ai_response.call_args
        passed_diff = args[0]
        self.assertTrue("[Diff truncated for length. Upgrade to Pro" in passed_diff)
        self.assertTrue(len(passed_diff) < 3000)

    @unittest.mock.patch("main.generate_ai_response")
    @unittest.mock.patch("config.is_pro_active")
    def test_diff_truncation_pro(self, mock_is_pro, mock_ai_response):
        mock_is_pro.return_value = True
        mock_ai_response.return_value = "feat: add dummy commit"
        
        long_diff = "a" * 3000
        main.generate_commit_message(long_diff, "model", "url", 90)
        
        # Check that the diff was not truncated since limit is 16000
        args, kwargs = mock_ai_response.call_args
        passed_diff = args[0]
        self.assertFalse("truncated" in passed_diff)
        self.assertEqual(len(passed_diff), 3000)

    @unittest.mock.patch("main.generate_ai_response")
    @unittest.mock.patch("config.is_pro_active")
    def test_free_commit_strips_body(self, mock_is_pro, mock_ai_response):
        mock_is_pro.return_value = False
        # AI returns a multi-line commit message
        mock_ai_response.return_value = "feat: add user\n\nDetailed explanation of user login"
        
        result = main.generate_commit_message("some diff", "model", "url", 90)
        self.assertEqual(result, "feat: add user")

    @unittest.mock.patch("main.generate_ai_response")
    @unittest.mock.patch("config.is_pro_active")
    def test_pro_commit_keeps_body(self, mock_is_pro, mock_ai_response):
        mock_is_pro.return_value = True
        mock_ai_response.return_value = "feat: add user\n\nDetailed explanation of user login"
        
        result = main.generate_commit_message("some diff", "model", "url", 90)
        self.assertEqual(result, "feat: add user\n\nDetailed explanation of user login")

    def test_wrap_body_lines_preserves_lists_and_wraps(self):
        msg = (
            "feat: add authentication\n"
            "\n"
            "- First item in list that is also extremely long and needs to be wrapped properly with its indent intact."
        )
        wrapped = main.wrap_body_lines(msg)
        lines = wrapped.splitlines()
        self.assertTrue(all(len(line) <= 72 for line in lines))
        # Find the list line and verify the subsequent line is indented
        idx = [i for i, l in enumerate(lines) if l.startswith("- First item")][0]
        self.assertTrue(lines[idx+1].startswith("  "))

    def test_wrap_body_lines_stops_at_first_paragraph(self):
        msg = (
            "feat: add authentication\n"
            "\n"
            "Line 1\n"
            "Line 2\n"
            "\n"
            "Line 4\n"
            "Line 5"
        )
        wrapped = main.wrap_body_lines(msg)
        lines = wrapped.splitlines()
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[2], "Line 1")
        self.assertEqual(lines[3], "Line 2")


if __name__ == "__main__":
    unittest.main()
