import importlib
import os
import sys
import unittest


class ProductionSettingsTests(unittest.TestCase):
    """Verify settings.py reads correctly from environment variables (SCRUM-22)."""

    def _reload_settings(self, env_overrides):
        """
        Temporarily set environment variables, reload assist.settings, and
        return the reloaded module.  Cleans up env and sys.modules afterward.
        """
        original_env = {}
        for key, value in env_overrides.items():
            original_env[key] = os.environ.get(key)
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

        # Force a fresh import of the settings module.
        if "assist.settings" in sys.modules:
            del sys.modules["assist.settings"]

        try:
            settings = importlib.import_module("assist.settings")
        finally:
            # Restore original environment.
            for key, original_value in original_env.items():
                if original_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_value
            if "assist.settings" in sys.modules:
                del sys.modules["assist.settings"]

        return settings

    # --- SECRET_KEY ---

    def test_secret_key_reads_from_environment_variable(self):
        settings = self._reload_settings({"SECRET_KEY": "test-secret-key-abc123"})
        self.assertEqual(settings.SECRET_KEY, "test-secret-key-abc123")

    def test_secret_key_falls_back_to_default_when_env_not_set(self):
        settings = self._reload_settings({"SECRET_KEY": None})
        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertNotEqual(settings.SECRET_KEY, "")

    # --- DEBUG ---

    def test_debug_is_false_by_default(self):
        settings = self._reload_settings({"DEBUG": None})
        self.assertFalse(settings.DEBUG)

    def test_debug_is_true_when_env_set_to_true(self):
        settings = self._reload_settings({"DEBUG": "True"})
        self.assertTrue(settings.DEBUG)

    def test_debug_is_false_when_env_set_to_false(self):
        settings = self._reload_settings({"DEBUG": "False"})
        self.assertFalse(settings.DEBUG)

    # --- ALLOWED_HOSTS ---

    def test_allowed_hosts_includes_localhost_always(self):
        settings = self._reload_settings({"RENDER_EXTERNAL_HOSTNAME": None})
        self.assertIn("localhost", settings.ALLOWED_HOSTS)
        self.assertIn("127.0.0.1", settings.ALLOWED_HOSTS)

    def test_render_hostname_added_to_allowed_hosts_when_env_set(self):
        settings = self._reload_settings(
            {"RENDER_EXTERNAL_HOSTNAME": "my-app.onrender.com"}
        )
        self.assertIn("my-app.onrender.com", settings.ALLOWED_HOSTS)

    def test_render_hostname_not_in_allowed_hosts_when_env_not_set(self):
        settings = self._reload_settings({"RENDER_EXTERNAL_HOSTNAME": None})
        for host in settings.ALLOWED_HOSTS:
            self.assertNotIn("onrender.com", host)

    # --- CSRF_TRUSTED_ORIGINS ---

    def test_render_origin_added_to_csrf_trusted_origins_when_env_set(self):
        settings = self._reload_settings(
            {"RENDER_EXTERNAL_HOSTNAME": "my-app.onrender.com"}
        )
        self.assertIn("https://my-app.onrender.com", settings.CSRF_TRUSTED_ORIGINS)

    def test_render_origin_not_in_csrf_trusted_origins_when_env_not_set(self):
        settings = self._reload_settings({"RENDER_EXTERNAL_HOSTNAME": None})
        for origin in settings.CSRF_TRUSTED_ORIGINS:
            self.assertNotIn("onrender.com", origin)
