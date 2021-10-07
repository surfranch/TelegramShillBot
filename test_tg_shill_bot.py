# stdlib
import unittest

# custom
import tg_shill_bot


class ValidateSettingsTest(unittest.TestCase):
    def test_load_settings(self):
        # assert bad yaml raises exception
        with self.assertRaises(Exception):
            tg_shill_bot.load_settings("resources/bad_settings.yml")

    def test_validate_account_settings(self):
        account_settings = {
            "api_id": 123,
            "api_hash": "some api hash",
            "app_short_name": "some app short name",
        }

        # assert legit returns none
        self.assertIsNone(tg_shill_bot.validate_account_settings(account_settings))

        bad_api_id = account_settings.copy()
        # assert bad api id raises exception
        with self.assertRaises(Exception):
            bad_api_id["api_id"] = "some api id"
            tg_shill_bot.validate_account_settings(bad_api_id)
        # assert api id required
        with self.assertRaises(Exception):
            bad_api_id.pop("api_id")
            tg_shill_bot.validate_account_settings(bad_api_id)

        bad_api_hash = account_settings.copy()
        # assert bad api hash raises exception
        with self.assertRaises(Exception):
            bad_api_hash["api_hash"] = 123
            tg_shill_bot.validate_account_settings(bad_api_hash)
        # assert api hash required
        with self.assertRaises(Exception):
            bad_api_hash.pop("api_hash")
            tg_shill_bot.validate_account_settings(bad_api_hash)

        bad_app_short_name = account_settings.copy()
        # assert bad app short name raises exception
        with self.assertRaises(Exception):
            bad_app_short_name["app_short_name"] = 123
            tg_shill_bot.validate_account_settings(bad_app_short_name)
        with self.assertRaises(Exception):
            bad_app_short_name.pop("app_short_name")
            tg_shill_bot.validate_account_settings(bad_app_short_name)


if __name__ == "__main__":
    unittest.main()
