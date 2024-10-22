import json
import pytest
import runregistry
from runregistry.runregistry import (
    get_run,
    get_runs,
    get_dataset_names_of_run,
    get_dataset,
    get_datasets,
    get_lumisections,
    get_oms_lumisections,
    get_lumisection_ranges,
    get_oms_lumisection_ranges,
    get_joint_lumisection_ranges,
    get_cycles,
    get_lumisection_ranges_by_component,
    get_datasets_accepted,
    create_json,
    setup,
)

VALID_RUN_NUMBER = 327743
VALID_RUN_RANGE_START = 309000
VALID_RUN_RANGE_STOP = 310000

INVALID_RUN_NUMBER = 420420420
VALID_DATASET_NAME = "/PromptReco/HICosmics18A/DQM"
INVALID_DATASET_NAME = "/PromptKikiriko/HELLOCosmics18Z/DQM"


def test_client_get_run():
    run_number = VALID_RUN_NUMBER
    run = get_run(run_number=VALID_RUN_NUMBER)
    assert run["run_number"] == VALID_RUN_NUMBER
    # Non-existent run
    run_number = INVALID_RUN_NUMBER
    run = get_run(run_number=run_number)
    assert not run


def test_client_get_runs_no_filter():
    with pytest.raises(Exception) as e:
        runs = get_runs()
    assert "must pass a filter" in e.exconly()


def test_client_get_runs():
    # Gets runs between run number VALID_RUN_RANGE_START and VALID_RUN_RANGE_STOP
    filter_run = {
        "run_number": {
            "and": [{">": VALID_RUN_RANGE_START}, {"<": VALID_RUN_RANGE_STOP}]
        }
    }
    runs = get_runs(filter=filter_run)
    assert len(runs) > 0
    # Gets runs that contain lumisections that classified DT as GOOD AND lumsiections that classified hcal as STANDBY
    filter_run = {
        "run_number": {
            "and": [{">": VALID_RUN_RANGE_START}, {"<": VALID_RUN_RANGE_STOP}]
        },
        "dt-dt": "GOOD",
        # 'hcal': 'STANDBY'
    }

    runs = get_runs(filter=filter_run)
    assert len(runs) > 0
    runs = []

    filter_run = {
        "run_number": {
            "and": [{">": VALID_RUN_RANGE_START}, {"<": VALID_RUN_RANGE_STOP}]
        },
        "tracker-strip": "GOOD",
    }
    runs = get_runs(filter=filter_run)
    print(json.dumps(runs))
    assert len(runs) > 0


def test_client_get_runs_with_ignore_filter():
    filter_run = {
        "run_number": {
            "and": [{">": VALID_RUN_RANGE_START}, {"<": VALID_RUN_RANGE_STOP}]
        },
        "oms_attributes.hlt_key": {"like": "%commissioning2018%"},
        "triplet_summary.dt-dt.GOOD": {">": 0},
    }
    runs = get_runs(filter=filter_run, ignore_filter_transformation=True)
    assert len(runs) > 0


def test_client_get_datasets_with_ignore_filter():
    # datasets = get_datasets(filter={
    #     "run_number": {
    #         "and": [{
    #             ">": VALID_RUN_RANGE_START
    #         }, {
    #             "<": VALID_RUN_RANGE_STOP
    #         }]
    #     },
    #     "oms_attributes.hlt_key": {
    #         "like": "%commissioning2018%"
    #     },
    #     "triplet_summary.dt-dt.GOOD": {
    #         ">": 0
    #     },
    # },
    #                         ignore_filter_transformation=True)

    datasets = get_datasets(
        filter={
            "and": [
                {
                    "run_number": {
                        "and": [
                            {">": VALID_RUN_RANGE_START},
                            {"<": VALID_RUN_RANGE_STOP},
                        ]
                    }
                }
            ],
            "name": {"and": [{"<>": "online"}]},
            "dataset_attributes.global_state": {
                "and": [{"or": [{"=": "OPEN"}, {"=": "SIGNOFF"}, {"=": "COMPLETED"}]}]
            },
        },
        ignore_filter_transformation=True,
    )
    assert len(datasets) > 0


# test_client_get_datasets_with_ignore_filter()

# test_client_get_runs_with_ignore_filter()


def test_client_get_runs_not_compressed():
    runs = get_runs(
        filter={
            "run_number": {
                "and": [{">": VALID_RUN_RANGE_START}, {"<": VALID_RUN_RANGE_STOP}]
            },
            "dt-dt": "GOOD",
        },
        compress_attributes=False,
    )
    assert len(runs) > 0


def get_runs_with_combined_filter():
    runs = get_runs(
        filter={
            "run_number": {
                "and": [{">": VALID_RUN_RANGE_START}, {"<": VALID_RUN_RANGE_STOP}]
                # },
                # 'hlt_key': {
                #     'like': '%commissioning2018%'
                # },
                # 'significant': {
                #     '=': True
            }
        }
    )
    assert len(runs) > 0


def test_client_get_dataset_names_of_run():
    dataset_names = get_dataset_names_of_run(run_number=VALID_RUN_NUMBER)
    assert len(dataset_names) > 0


def test_client_get_dataset():
    dataset = get_dataset(run_number=VALID_RUN_NUMBER, dataset_name=VALID_DATASET_NAME)
    assert dataset["run_number"] == VALID_RUN_NUMBER
    assert dataset["name"] == VALID_DATASET_NAME
    dataset = get_dataset(
        run_number=INVALID_RUN_NUMBER, dataset_name=INVALID_DATASET_NAME
    )
    assert not dataset


def test_client_get_datasets_no_limit():
    datasets = get_datasets(
        compress_attributes=True,
        filter={
            "run_number": {
                "and": [{">": VALID_RUN_RANGE_START}, {"<": VALID_RUN_RANGE_STOP}]
            }
        },
    )
    assert len(datasets) > 0
    assert "Run" not in datasets[0]


def test_client_get_datasets_no_compression():
    datasets = get_datasets(
        compress_attributes=False,
        filter={
            "run_number": {
                "and": [{">": VALID_RUN_RANGE_START}, {"<": VALID_RUN_RANGE_STOP}]
            }
        },
    )
    assert len(datasets) > 0
    assert "Run" in datasets[0]


def test_client_get_datasets_with_limit():
    datasets = get_datasets(
        limit=5,
        filter={
            "run_number": {
                "and": [{">": VALID_RUN_RANGE_START}, {"<": VALID_RUN_RANGE_STOP}]
            }
        },
    )
    assert len(datasets) > 0


def test_client_get_datasets_no_filters():
    with pytest.raises(Exception) as e:
        datasets = get_datasets()
    assert "must pass a filter" in e.exconly()


def test_client_get_lumisections():
    lumisections = get_lumisections(VALID_RUN_NUMBER, VALID_DATASET_NAME)
    assert len(lumisections) > 0


def test_client_get_oms_lumisections():
    lumisections = get_oms_lumisections(VALID_RUN_NUMBER)
    assert len(lumisections) > 0
    dataset_lumisections = get_oms_lumisections(VALID_RUN_NUMBER, VALID_DATASET_NAME)
    assert len(dataset_lumisections) > 0


def test_client_get_lumisection_ranges():
    lumisections = get_lumisection_ranges(VALID_RUN_NUMBER, VALID_DATASET_NAME)
    assert len(lumisections) > 0


def test_client_get_oms_lumisection_ranges():
    lumisections = get_oms_lumisection_ranges(VALID_RUN_NUMBER)
    assert len(lumisections) > 0


def test_client_get_joint_lumisection_ranges():
    lumisections = get_joint_lumisection_ranges(VALID_RUN_NUMBER, VALID_DATASET_NAME)
    assert len(lumisections) > 0


def test_client_get_collisions18():
    runs = get_runs(filter={"class": "Collisions18"})
    assert len(runs) > 0


def test_client_get_or_run():
    runs = get_runs(filter={"run_number": {"or": [VALID_RUN_NUMBER]}})


def test_client_get_datasets_with_filter():
    datasets = get_datasets(
        filter={
            "run_number": {
                "and": [{">": VALID_RUN_RANGE_START}, {"<": VALID_RUN_RANGE_STOP}]
            },
            "tracker-strip": "GOOD",
        }
    )
    assert len(datasets) > 0


json_logic = {
    "and": [
        {">=": [{"var": "run.oms.energy"}, 6000]},
        {"<=": [{"var": "run.oms.energy"}, 7000]},
        {">=": [{"var": "run.oms.b_field"}, 3.7]},
        {"in": ["25ns", {"var": "run.oms.injection_scheme"}]},
        {"==": [{"in": ["WMass", {"var": "run.oms.hlt_key"}]}, False]},
        {"==": [{"var": "lumisection.rr.dt-dt"}, "GOOD"]},
        {"==": [{"var": "lumisection.rr.csc-csc"}, "GOOD"]},
        {"==": [{"var": "lumisection.rr.l1t-l1tmu"}, "GOOD"]},
        {"==": [{"var": "lumisection.rr.l1t-l1tcalo"}, "GOOD"]},
        {"==": [{"var": "lumisection.rr.hlt-hlt"}, "GOOD"]},
        {"==": [{"var": "lumisection.oms.bpix_ready"}, True]},
    ]
}


def test_client_create_json():
    json = create_json(
        json_logic=json_logic, dataset_name_filter="/PromptReco/Collisions2018A/DQM"
    )
    print(json)


def test_client_custom_filter():
    filter_arg = {
        "dataset_name": {"like": "%/PromptReco/Cosmics18CRUZET%"},
        "run_number": {
            "and": [{">=": VALID_RUN_RANGE_START}, {"<=": VALID_RUN_RANGE_STOP}]
        },
        "class": {"like": "Cosmics18CRUZET"},
        "global_state": {"like": "COMPLETED"},
        "ecal-ecal": "EXCLUDED",
    }

    datasets = get_datasets(filter=filter_arg)
    assert datasets


def test_client_setup_random():
    with pytest.raises(Exception) as e:
        setup("Olo kaskarikes mas kaneis")
    assert "Invalid setup target" in e.exconly()


def test_client_setup_production():
    setup("production")
    assert "https://cmsrunregistry" in runregistry.runregistry.api_url


def test_client_setup_development():
    setup("development")
    assert "https://dev-cmsrunregistry" in runregistry.runregistry.api_url


def test_client_get_cycles():
    answers = get_cycles()
    assert len(answers) > 0
    assert "id_cycle" in answers[0]
    assert "cycle_name" in answers[0]
    assert "cycle_attributes" in answers[0]
    assert "deadline" in answers[0]
    assert "datasets" in answers[0]


def test_client_get_lumisection_ranges_by_component():
    answer = get_lumisection_ranges_by_component(VALID_RUN_NUMBER)
    assert len(answer.keys()) > 0
    assert "dt-dt" in answer
    assert "rpc-hv" in answer
    assert "tracker-track_private" in answer


def test_client_get_datasets_accepted():
    answers = get_datasets_accepted()
    assert len(answers) > 0
    assert isinstance(answers[0], dict)
    assert "regexp" in answers[0]
    assert "id" in answers[0]
    assert "name" in answers[0]
    assert "class" in answers[0]
