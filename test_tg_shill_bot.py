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
            "phone_number": "+18675309",
            "messages": {},
            "raid": {},
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

        bad_phone_number = account_settings.copy()
        # assert bad phone number raises exception
        with self.assertRaises(Exception):
            bad_phone_number["phone_number"] = 123
            tg_shill_bot.validate_account_settings(bad_phone_number)
        with self.assertRaises(Exception):
            bad_app_short_name.pop("phone_number")
            tg_shill_bot.validate_account_settings(bad_phone_number)

        bad_messages = account_settings.copy()
        # assert bad messages raises exception
        with self.assertRaises(Exception):
            bad_messages["messages"] = []
            tg_shill_bot.validate_account_settings(bad_messages)
        with self.assertRaises(Exception):
            bad_messages.pop("messages")
            tg_shill_bot.validate_account_settings(bad_messages)

        bad_raid = account_settings.copy()
        # assert bad raid raises exception
        with self.assertRaises(Exception):
            bad_raid["raid"] = []
            tg_shill_bot.validate_account_settings(bad_raid)
        with self.assertRaises(Exception):
            bad_raid.pop("raid")
            tg_shill_bot.validate_account_settings(bad_raid)

    def test_validate_messages_settings(self):
        messages_settings = {
            "TesT_123": "this is a legit thing",
        }

        # assert legit returns none
        self.assertIsNone(tg_shill_bot.validate_messages_settings(messages_settings))

        bad_key = messages_settings.copy()
        # assert bad key raises exception
        with self.assertRaises(Exception):
            bad_key["bad-key"] = "some bad key"
            tg_shill_bot.validate_messages_settings(bad_key)

        bad_value = messages_settings.copy()
        # assert bad value raises exception
        with self.assertRaises(Exception):
            bad_value["bad_value"] = ["some bad value"]
            tg_shill_bot.validate_messages_settings(bad_value)

    def test_validate_raid_settings(self):
        raid_settings = {
            "message_type": "Some_Me55age_Type",
            "wait_interval": 123,
            "increase_wait_interval": 123,
            "image": "images/cd.jpg",
        }

        # assert legit returns none
        legit = {"test-raid": raid_settings}
        self.assertIsNone(tg_shill_bot.validate_raid_settings(legit))

        bad_wait_interval = {"test-raid": raid_settings.copy()}
        # assert bad wait interval raises exception
        with self.assertRaises(Exception):
            bad_wait_interval["test-raid"]["wait_interval"] = "123"
            tg_shill_bot.validate_raid_settings(bad_wait_interval)

        bad_increase_wait_interval = {"test-raid": raid_settings.copy()}
        # assert bad increase wait interval raises exception
        with self.assertRaises(Exception):
            bad_increase_wait_interval["test-raid"]["increase_wait_interval"] = "123"
            tg_shill_bot.validate_raid_settings(bad_increase_wait_interval)

        bad_image = {"test-raid": raid_settings.copy()}
        # assert bad image raises exception
        with self.assertRaises(Exception):
            bad_image["test-raid"]["image"] = 123
            tg_shill_bot.validate_raid_settings(bad_image)


if __name__ == "__main__":
    unittest.main()
