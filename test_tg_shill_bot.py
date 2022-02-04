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
            "splay": 7,
            "messages": {},
            "raid": {},
            "random_message_format": 'lambda x : x + "!"',
            "random_message": [],
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
            bad_phone_number.pop("phone_number")
            tg_shill_bot.validate_account_settings(bad_phone_number)

        bad_splay = account_settings.copy()
        # assert bad splay raises exception
        with self.assertRaises(Exception):
            bad_splay["splay"] = "123"
            tg_shill_bot.validate_account_settings(bad_splay)
        with self.assertRaises(Exception):
            bad_splay.pop("splay")
            tg_shill_bot.validate_account_settings(bad_splay)

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

        bad_random_message = account_settings.copy()
        # assert bad random message raises exception
        with self.assertRaises(Exception):
            bad_random_message["random_message"] = {}
            tg_shill_bot.validate_account_settings(bad_random_message)
        with self.assertRaises(Exception):
            bad_random_message.pop("random_message")
            tg_shill_bot.validate_account_settings(bad_random_message)

        bad_random_message_format = account_settings.copy()
        # assert bad random message format raises exception
        with self.assertRaises(Exception):
            bad_random_message_format["random_message_format"] = {}
            tg_shill_bot.validate_account_settings(bad_random_message_format)
        with self.assertRaises(Exception):
            bad_random_message_format.pop("random_message_format")
            tg_shill_bot.validate_account_settings(bad_random_message_format)

    def test_validate_random_message_settings(self):
        random_message_settings = [
            "hello",
            "world",
        ]

        # assert legit returns none
        self.assertIsNone(
            tg_shill_bot.validate_random_message_settings(random_message_settings)
        )

        # assert empty random message raises exception
        with self.assertRaises(Exception):
            tg_shill_bot.validate_random_message_settings([])

        # assert random message with nums raises exception
        with self.assertRaises(Exception):
            tg_shill_bot.validate_random_message_settings([1])

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
            "total_messages": 123,
            "image": "images/cd.jpg",
        }

        # assert legit single message type returns none
        legit = {"test-raid": raid_settings}
        self.assertIsNone(tg_shill_bot.validate_raid_settings(legit))
        # assert legit many message types returns none
        legit["test-raid"]["message_type"] = [
            "Some_Me55age_Type1",
            "Some_Me55age_Type2",
            "Some_Me55age_Type3",
        ]
        self.assertIsNone(tg_shill_bot.validate_raid_settings(legit))

        bad_wait_interval = {"test-raid": raid_settings.copy()}
        # assert bad wait interval raises exception
        with self.assertRaises(Exception):
            bad_wait_interval["test-raid"]["wait_interval"] = "123"
            tg_shill_bot.validate_raid_settings(bad_wait_interval)
        with self.assertRaises(Exception):
            bad_wait_interval["test-raid"]["wait_interval"] = 0
            tg_shill_bot.validate_raid_settings(bad_wait_interval)

        bad_increase_wait_interval = {"test-raid": raid_settings.copy()}
        # assert bad increase wait interval raises exception
        with self.assertRaises(Exception):
            bad_increase_wait_interval["test-raid"]["increase_wait_interval"] = "123"
            tg_shill_bot.validate_raid_settings(bad_increase_wait_interval)
        with self.assertRaises(Exception):
            bad_increase_wait_interval["test-raid"]["increase_wait_interval"] = 0
            tg_shill_bot.validate_raid_settings(bad_increase_wait_interval)

        bad_total_messages = {"test-raid": raid_settings.copy()}
        # assert bad total messages raises exception
        with self.assertRaises(Exception):
            bad_total_messages["test-raid"]["total_messages"] = "123"
            tg_shill_bot.validate_raid_settings(bad_total_messages)
        with self.assertRaises(Exception):
            bad_total_messages["test-raid"]["total_messages"] = 0
            tg_shill_bot.validate_raid_settings(bad_total_messages)

        bad_image = {"test-raid": raid_settings.copy()}
        # assert bad image raises exception
        with self.assertRaises(Exception):
            bad_image["test-raid"]["image"] = 123
            tg_shill_bot.validate_raid_settings(bad_image)

    def test_randomize_message(self):
        channel = {
            "message": ["message 1"],
            "last_message": 0,
        }
        ty1 = "ty1"
        ty2 = "ty2"
        message = tg_shill_bot.randomize_message(channel, ty1, ty2)

        self.assertIn(channel["message"][0], message)
        self.assertIn(ty1, message)
        self.assertIn(ty2, message)

    def test_random_message(self):
        rm = tg_shill_bot.random_message()

        self.assertIn(rm, tg_shill_bot.random_messages())

    def test_next_message(self):
        start = 0
        channel = {"last_message": start, "message": ["msg1", "msg2"]}
        message, channel = tg_shill_bot.next_message(channel)
        self.assertIn(channel["message"][channel["last_message"]], message)
        self.assertEqual(channel["last_message"], start + 1)

    def test_resolve_total_messages(self):
        go_chl = {"count": 1, "total_messages": 3, "loop": True}
        stop_chl1 = {"count": 3, "total_messages": 3, "loop": True}
        stop_chl2 = {"count": 4, "total_messages": 3, "loop": True}
        self.assertEqual(tg_shill_bot.resolve_total_messages(go_chl)["loop"], True)
        self.assertEqual(tg_shill_bot.resolve_total_messages(stop_chl1)["loop"], False)
        self.assertEqual(tg_shill_bot.resolve_total_messages(stop_chl2)["loop"], False)

    def test_log_green(self):
        self.assertIn(
            tg_shill_bot.Style.GREEN.value, tg_shill_bot.log_green("i am green")
        )

    def test_log_yellow(self):
        self.assertIn(
            tg_shill_bot.Style.YELLOW.value, tg_shill_bot.log_yellow("i am yellow")
        )

    def test_log_red(self):
        self.assertIn(tg_shill_bot.Style.RED.value, tg_shill_bot.log_red("i am red"))

    def test_header(self):
        self.assertIn(tg_shill_bot.Style.CYAN.value, tg_shill_bot.header())


if __name__ == "__main__":
    unittest.main()
