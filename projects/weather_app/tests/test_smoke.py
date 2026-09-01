import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import main


class WeatherTests(unittest.TestCase):
    @patch("main.fetch_json")
    def test_weather_report_is_formatted(self, mocked_fetch):
        mocked_fetch.side_effect = [
            {"results": [{"name": "Delhi", "admin1": "Delhi", "country": "India", "latitude": 28.6, "longitude": 77.2}]},
            {"current": {"temperature_2m": 30, "apparent_temperature": 33, "relative_humidity_2m": 60, "weather_code": 1, "wind_speed_10m": 12, "time": "2026-08-20T10:00"}},
        ]
        text = main.format_weather(main.get_current_weather("Delhi"))
        self.assertIn("Weather for Delhi, Delhi, India", text)
        self.assertIn("Mostly clear", text)

    @patch("main.fetch_json", return_value={"results": []})
    def test_missing_city_is_clear_error(self, _mocked_fetch):
        with self.assertRaises(main.WeatherError):
            main.find_location("Not A City")
