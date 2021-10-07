# stdlib
import unittest

# import tg_shill_bot
import jsonschema


class ValidateSettingsTest(unittest.TestCase):
    def test_something(self):
        jsonschema.validate(
            {
                "api_id": 123,
                "api_hash": "qwe",
                "app_short_name": "qwe",
                "messages": {"one": "hello world"},
            },
            {
                "type": "object",
                "properties": {
                    "api_id": {"type": "number"},
                    "api_hash": {"type": "string"},
                    "app_short_name": {"type": "string"},
                    "messages": {
                        "type": "object",
                        "minProperties": 1,
                    },
                },
                "required": [
                    "api_id",
                    "api_hash",
                    "app_short_name",
                    "messages",
                ],
            },
        )
        # tg_shill_bot.validate_settings({
        #     "api_id1": 123
        # })
        a = True
        self.assertTrue(a)


if __name__ == "__main__":
    unittest.main()
