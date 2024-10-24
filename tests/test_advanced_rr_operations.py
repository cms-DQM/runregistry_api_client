import pytest
import logging
import runregistry

logger = logging.getLogger(__name__)
VALID_RUN_NUMBER = 362874
VALID_DATASET_NAME = "/PromptReco/Commissioning2021/DQM"
EGROUPS_ERROR = "User needs to be part of any of the following e-groups"


@pytest.fixture
def setup_runregistry():
    logger.info("Connecting to development runregistry")
    runregistry.setup("development")


def test_advanced_move_datasets(setup_runregistry):
    with pytest.raises(Exception) as e:
        answers = runregistry.move_datasets(
            from_=runregistry.WAITING_DQM_GUI_CONSTANT,
            to_="OPEN",
            dataset_name=VALID_DATASET_NAME,
            run=VALID_RUN_NUMBER,
            workspace="global",
        )
    assert EGROUPS_ERROR in e.exconly()
    # TODO: Run also with a token that has permission
    with pytest.raises(Exception) as e:
        # Requires permission
        answers = runregistry.move_datasets(
            from_="OPEN",
            to_="SIGNOFF",
            dataset_name=VALID_DATASET_NAME,
            run=VALID_RUN_NUMBER,
            workspace="ctpps",
        )
    assert EGROUPS_ERROR in e.exconly()


def test_advanced_move_datasets_bad_from(setup_runregistry):
    with pytest.raises(ValueError):
        answers = runregistry.move_datasets(
            from_="MPAMIES",
            to_="SIGNOFF",
            dataset_name=VALID_DATASET_NAME,
            run=VALID_RUN_NUMBER,
            workspace="global",
        )


def test_advanced_move_datasets_no_run(setup_runregistry):
    with pytest.raises(ValueError):
        answers = runregistry.move_datasets(
            from_="MPAMIES",
            to_="SIGNOFF",
            dataset_name=VALID_DATASET_NAME,
            workspace="global",
        )


def test_advanced_move_datasets_bad_to(setup_runregistry):
    with pytest.raises(ValueError):
        answers = runregistry.move_datasets(
            from_=runregistry.WAITING_DQM_GUI_CONSTANT,
            to_="AGKINARES",
            dataset_name=VALID_DATASET_NAME,
            run=VALID_RUN_NUMBER,
            workspace="global",
        )


def test_advanced_make_significant_single_run(setup_runregistry):
    # Get latest run in dev runregistry and make it significant
    run = runregistry.get_runs(limit=1, filter={})[0]
    with pytest.raises(Exception) as e:
        # requires permission
        runregistry.make_significant_runs(run=run["run_number"])
    assert EGROUPS_ERROR in e.exconly()


def test_advanced_make_significant_multi_runs(setup_runregistry):
    # Get latest run in dev runregistry and make it significant
    run = runregistry.get_runs(limit=1, filter={})[0]
    with pytest.raises(Exception) as e:
        # requires permission
        runregistry.make_significant_runs(runs=[run["run_number"]])
    assert EGROUPS_ERROR in e.exconly()


def test_advanced_make_significant_no_runs(setup_runregistry):
    run = runregistry.get_runs(limit=1, filter={})[0]
    with pytest.raises(ValueError):
        # Required args missing
        runregistry.make_significant_runs()


def test_advanced_reset_RR_attributes_and_refresh_runs_signed_off(setup_runregistry):
    with pytest.raises(Exception) as e:
        # Cannot refresh runs which are not open
        answers = runregistry.reset_RR_attributes_and_refresh_runs(
            runs=VALID_RUN_NUMBER
        )
    assert "Run must be in state OPEN" in repr(e)


def test_advanced_reset_RR_attributes_and_refresh_runs_no_run(setup_runregistry):
    with pytest.raises(ValueError) as e:
        # Cannot refresh runs which are not open
        answers = runregistry.reset_RR_attributes_and_refresh_runs()


def test_advanced_reset_RR_attributes_and_refresh_runs_open(setup_runregistry):
    run = runregistry.get_runs(limit=1, filter={})[0]
    answers = runregistry.reset_RR_attributes_and_refresh_runs(runs=run["run_number"])
    assert isinstance(answers, list)


def test_advanced_manually_refresh_components_statuses_for_no_runs(setup_runregistry):
    with pytest.raises(ValueError):
        # Missing argument
        runregistry.manually_refresh_components_statuses_for_runs()


def test_advanced_manually_refresh_components_statuses_for_runs_open(setup_runregistry):
    run = runregistry.get_runs(limit=1, filter={})[0]
    # Currently, manual refresh does not need special permissions??
    answers = runregistry.manually_refresh_components_statuses_for_runs(
        runs=run["run_number"]
    )
    assert isinstance(answers, list)


def test_advanced_manually_refresh_components_statuses_for_runs_signed_off(
    setup_runregistry,
):
    with pytest.raises(Exception) as e:
        runregistry.manually_refresh_components_statuses_for_runs(runs=VALID_RUN_NUMBER)
    assert "Run must be in state OPEN" in e.exconly()


def test_advanced_move_runs_no_run_arg(setup_runregistry):
    with pytest.raises(ValueError):
        # Raises ValueError
        runregistry.move_runs("OPEN", "SIGNOFF")


def test_advanced_move_single_run(setup_runregistry):
    with pytest.raises(Exception) as e:
        # Requires permission
        runregistry.move_runs("OPEN", "SIGNOFF", run=VALID_RUN_NUMBER)
    assert "User needs to be part of any of the following e-groups" in e.exconly()


def test_advanced_move_multi_runs(setup_runregistry):
    with pytest.raises(Exception) as e:
        # Requires permission
        runregistry.move_runs("OPEN", "SIGNOFF", runs=[VALID_RUN_NUMBER])
    assert EGROUPS_ERROR in e.exconly()


def test_advanced_move_runs_invalid(setup_runregistry):
    with pytest.raises(ValueError):
        # Requires permission
        runregistry.move_runs("!!!!", "???", runs=[VALID_RUN_NUMBER])


def test_advanced_edit_rr_lumisections_good(setup_runregistry):
    with pytest.raises(Exception) as e:
        # Requires permission
        runregistry.edit_rr_lumisections(
            VALID_RUN_NUMBER, 0, 1, "castor-castor", "GOOD"
        )
    assert "User needs to be part of any of the following e-groups" in e.exconly()


def test_advanced_edit_rr_lumisections_bad(setup_runregistry):
    with pytest.raises(ValueError):
        # Requires permission
        runregistry.edit_rr_lumisections(
            VALID_RUN_NUMBER, 0, 1, "castor-castor", "KALHSPERA STHN PAREA ;)"
        )


def test_advanced_change_run_class_list(setup_runregistry):
    with pytest.raises(Exception) as e:
        # Requires permission
        runregistry.change_run_class(run_numbers=[VALID_RUN_NUMBER], new_class="test")
    assert "User needs to be part of any of the following e-groups" in e.exconly()


def test_advanced_change_run_class_int(setup_runregistry):
    """
    Current behavior is to accept both a list and an int as run_numbers
    """
    with pytest.raises(Exception) as e:
        # Still Requires permission
        runregistry.change_run_class(run_numbers=VALID_RUN_NUMBER, new_class="test")
    assert "User needs to be part of any of the following e-groups" in e.exconly()


def test_advanced_change_run_class_list_with_bad_run_types(setup_runregistry):
    with pytest.raises(ValueError) as e:
        runregistry.change_run_class(run_numbers=["3455555"], new_class="test")


def test_advanced_change_run_class_bad_run_numbers(setup_runregistry):
    with pytest.raises(ValueError):
        runregistry.change_run_class(run_numbers="3455555", new_class="test")


def test_advanced_change_run_class_bad_new_class_type(setup_runregistry):
    with pytest.raises(ValueError):
        # Requires permission
        runregistry.change_run_class(run_numbers=[VALID_RUN_NUMBER], new_class=1)
