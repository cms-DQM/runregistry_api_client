import sys
import pytest
import requests
from runregistry.utils import transform_to_rr_run_filter
from runregistry.runregistry import (
    __version__,
    _get_user_agent,
    _get_headers,
    _get_token,
    _get_target,
    setup,
)


class TestFilterCreation:
    def test_get_run(self):
        run_number = 323434
        assert transform_to_rr_run_filter(run_filter={"run_number": run_number}) == {
            "run_number": {"=": run_number}
        }

    def test_get_multiple_run_using_or(self):
        run_number1 = 323555
        run_number2 = 323444
        run_number3 = 343222
        run_number4 = 333333
        user_input = {
            "run_number": {
                "or": [run_number1, run_number2, run_number3, {"=": run_number4}]
            }
        }
        desired_output = {
            "run_number": {
                "or": [
                    {"=": run_number1},
                    {"=": run_number2},
                    {"=": run_number3},
                    {"=": run_number4},
                ]
            }
        }

        assert transform_to_rr_run_filter(run_filter=user_input) == desired_output


class TestUtils:
    def test_user_agent(self):
        ua = _get_user_agent()
        assert (
            __version__ in ua
            and "runregistry_api_client" in ua
            and f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            in ua
            and requests.__version__ in ua
            and "zodiac sign" not in ua
        )

    def test_runregistry_setup(self):
        for target in ["development", "local", "production"]:
            setup(target)

            assert _get_target() == target

        with pytest.raises(Exception):
            setup("HAHAHAHA >:)")

    def test_headers(self):
        headers = _get_headers(token="WHATEVER :/")
        assert all(
            [key in headers for key in ["User-Agent", "Authorization", "Content-type"]]
        )

    def test_get_token(self):
        setup("local")
        assert _get_token() == ""
