import sys
import pytest
import requests
from runregistry.utils import (
    transform_to_rr_run_filter,
    transform_to_rr_dataset_filter,
    dataset_triplet_attributes,
    run_rr_attributes,
)
from runregistry.attributes import (
    run_oms_attributes,
    run_triplet_attributes,
    dataset_attributes,
)
from runregistry.runregistry import (
    __version__,
    _get_user_agent,
    _get_headers,
    _get_token,
    _get_target,
    __parse_runs_arg as _parse_runs_arg,
    setup,
)


class TestRunRegistryFilterCreation:
    def test_get_run(self):
        run_number = 323434
        assert transform_to_rr_run_filter(run_filter={"run_number": run_number}) == {
            "run_number": {"=": run_number}
        }

    def test_transform_triplets(self):
        VALID_VALUES = ["GOOD", "BAD", "STANDBY", "EXCLUDED", "NOTSET", "EMPTY"]
        for attribute in run_triplet_attributes:
            for value in VALID_VALUES:
                result = transform_to_rr_run_filter(
                    run_filter={attribute: {"=": value}}
                )
                assert f"triplet_summary.{attribute}.{value}" in result
        with pytest.raises(Exception):
            transform_to_rr_run_filter(run_filter={"ecal-ecal": {"=": "HEHEHE"}})

    def test_transform_invalid_attribute(self):
        with pytest.raises(Exception):
            transform_to_rr_run_filter(run_filter={"BRE KAKOS MPELAS": {"=": "HEHEHE"}})
        assert not transform_to_rr_run_filter(None)
        assert not transform_to_rr_run_filter("")
        assert not transform_to_rr_run_filter("SDF")
        assert not transform_to_rr_run_filter(15)

    def test_transform_attributes(self):
        VALID_ATTRIBUTES = [
            "rr_attributes",
            "oms_attributes",
            "triplet_summary",
            "triplet_summaryalksjdflkajsd",  # Unsure why this should be supported
        ]
        FILTER = {"=": "aaa"}
        for attribute in VALID_ATTRIBUTES:
            result = transform_to_rr_run_filter(run_filter={attribute: FILTER})
            assert attribute in result and result[attribute] == FILTER

    def test_transform_run_oms_attributes(self):

        FILTER = {"=": "test"}
        for attribute in run_oms_attributes:
            if attribute == "run_number":
                print(
                    "run_number seems to exist on both run_oms_attributes and "
                    + "run_triplet_attributes, meaning that run_number cannot "
                    + "be used with run_oms_attributes, only triplets"
                )
                continue
            result = transform_to_rr_run_filter(run_filter={attribute: FILTER})
            assert (
                f"oms_attributes.{attribute}" in result
                and result[f"oms_attributes.{attribute}"] == FILTER
            )

    def test_transform_run_rr_attributes(self):
        FILTER = {"=": "test"}
        for attribute in run_rr_attributes:
            result = transform_to_rr_run_filter(run_filter={attribute: FILTER})
            assert (
                f"rr_attributes.{attribute}" in result
                and result[f"rr_attributes.{attribute}"] == FILTER
            )

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


class TestDatasetFilterCreation:
    def test_dataset_attributes(self):
        FILTER = {"=": "aaa"}
        for attribute in dataset_attributes:
            result = transform_to_rr_dataset_filter(dataset_filter={attribute: FILTER})
            assert (
                f"dataset_attributes.{attribute}" in result
                and result[f"dataset_attributes.{attribute}"] == FILTER
            )

    def test_dataset_triplet_attributes_valid(self):
        VALID_VALUES = ["GOOD", "BAD", "STANDBY", "EXCLUDED", "NOTSET", "EMPTY"]
        for value in VALID_VALUES:
            for attribute in dataset_triplet_attributes:
                result = transform_to_rr_dataset_filter(
                    dataset_filter={attribute: {"=": value}}
                )
                assert f"triplet_summary.{attribute}.{value}" in result

    def test_dataset_triplet_attributes_invalid(self):
        with pytest.raises(Exception):
            transform_to_rr_dataset_filter(
                dataset_filter={dataset_triplet_attributes[0]: {"=": "ZE MALESI :("}}
            )

    def test_transform_run_oms_attributes(self):
        FILTER = {"=": "test"}
        for attribute in run_oms_attributes:
            if attribute == "run_number":
                print(
                    "run_number seems to exist on both run_oms_attributes and "
                    + "run_triplet_attributes, meaning that run_number cannot "
                    + "be used with run_oms_attributes, only triplets"
                )
                continue
            result = transform_to_rr_dataset_filter(dataset_filter={attribute: FILTER})
            assert (
                f"oms_attributes.{attribute}" in result
                and result[f"oms_attributes.{attribute}"] == FILTER
            )

    def test_transform_run_rr_attributes(self):
        FILTER = {"=": "test"}
        for attribute in run_rr_attributes:
            result = transform_to_rr_dataset_filter(dataset_filter={attribute: FILTER})
            assert (
                f"rr_attributes.{attribute}" in result
                and result[f"rr_attributes.{attribute}"] == FILTER
            )

    def test_transform_invalid_attribute(self):
        with pytest.raises(Exception):
            transform_to_rr_dataset_filter(
                dataset_filter={"BRE KAKOS MPELAS": {"=": "HEHEHE"}}
            )
        assert not transform_to_rr_dataset_filter(None)
        assert not transform_to_rr_dataset_filter("")
        assert not transform_to_rr_dataset_filter("SDF")
        assert not transform_to_rr_dataset_filter(15)


class TestUtils:
    MAGIC_RUN = 255525

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

    def test_parse_runs_int(self):
        runs = _parse_runs_arg(self.MAGIC_RUN)
        assert isinstance(runs, list) and runs[0] == self.MAGIC_RUN

    def test_parse_runs_str_int(self):
        runs = _parse_runs_arg(str(self.MAGIC_RUN))
        assert isinstance(runs, list) and runs[0] == self.MAGIC_RUN

    def test_parse_runs_str_str(self):
        runs = _parse_runs_arg("LMAO ://////////")
        assert isinstance(runs, list) and len(runs) == 0

    def test_parse_runs_list_int(self):
        runs = _parse_runs_arg([self.MAGIC_RUN, self.MAGIC_RUN + 1])
        assert isinstance(runs, list) and len(runs) == 2

    def test_parse_runs_list_str(self):
        # This case should probably be fixed to only accept list of ints
        runs = _parse_runs_arg([str(self.MAGIC_RUN), str(self.MAGIC_RUN + 1)])
        assert isinstance(runs, list) and len(runs) == 2

    def test_parse_runs_dict(self):
        runs = _parse_runs_arg({self.MAGIC_RUN})
        assert isinstance(runs, list) and len(runs) == 0
