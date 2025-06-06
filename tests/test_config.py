import os
import unittest
from unittest.mock import patch

from src.common.config import Config


class TestConfigEnvironmentOverrides(unittest.TestCase):
    """Tests for Config environment variable handling."""

    def test_env_used_when_missing(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}):
            cfg = Config()
            self.assertEqual(cfg.openai_api_key, "env-key")

    def test_explicit_argument_preserved(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}):
            cfg = Config(openai_api_key="explicit-key")
            self.assertEqual(cfg.openai_api_key, "explicit-key")


if __name__ == "__main__":
    unittest.main()
