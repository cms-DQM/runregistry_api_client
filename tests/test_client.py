import json
import warnings

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
    generate_json,
    create_json,
    setup,
)

VALID_RUN_NUMBER = 327743
VALID_RUN_RANGE_START = 309000
VALID_RUN_RANGE_STOP = 310000

INVALID_RUN_NUMBER = 420420420
VALID_DATASET_NAME = "/PromptReco/HICosmics18A/DQM"
INVALID_DATASET_NAME = "/PromptKikiriko/HELLOCosmics18Z/DQM"


def test_get_run():
    run_number = VALID_RUN_NUMBER
    run = get_run(run_number=VALID_RUN_NUMBER)
    assert run["run_number"] == VALID_RUN_NUMBER
    # Non-existent run
    run_number = INVALID_RUN_NUMBER
    run = get_run(run_number=run_number)
    assert not run


def test_get_runs():
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


def test_get_runs_with_ignore_filter():
    filter_run = {
        "run_number": {
            "and": [{">": VALID_RUN_RANGE_START}, {"<": VALID_RUN_RANGE_STOP}]
        },
        "oms_attributes.hlt_key": {"like": "%commissioning2018%"},
        "triplet_summary.dt-dt.GOOD": {">": 0},
    }
    runs = get_runs(filter=filter_run, ignore_filter_transformation=True)
    assert len(runs) > 0


def test_get_datasets_with_ignore_filter():
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


# test_get_datasets_with_ignore_filter()

# test_get_runs_with_ignore_filter()


def test_get_runs_not_compressed():
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


def test_get_dataset_names_of_run():
    dataset_names = get_dataset_names_of_run(run_number=VALID_RUN_NUMBER)
    assert len(dataset_names) > 0


def test_get_dataset():
    dataset = get_dataset(run_number=VALID_RUN_NUMBER, dataset_name=VALID_DATASET_NAME)
    assert dataset["run_number"] == VALID_RUN_NUMBER
    assert dataset["name"] == VALID_DATASET_NAME
    dataset = get_dataset(
        run_number=INVALID_RUN_NUMBER, dataset_name=INVALID_DATASET_NAME
    )
    assert not dataset


def test_get_datasets():
    datasets = get_datasets(
        filter={
            "run_number": {
                "and": [{">": VALID_RUN_RANGE_START}, {"<": VALID_RUN_RANGE_STOP}]
            }
        }
    )
    assert len(datasets) > 0


def test_get_lumisections():
    lumisections = get_lumisections(VALID_RUN_NUMBER, VALID_DATASET_NAME)
    assert len(lumisections) > 0


def test_get_oms_lumisections():
    lumisections = get_oms_lumisections(VALID_RUN_NUMBER)
    assert len(lumisections) > 0
    dataset_lumisections = get_oms_lumisections(VALID_RUN_NUMBER, VALID_DATASET_NAME)
    assert len(dataset_lumisections) > 0


def test_get_lumisection_ranges():
    lumisections = get_lumisection_ranges(VALID_RUN_NUMBER, VALID_DATASET_NAME)
    assert len(lumisections) > 0


def test_get_oms_lumisection_ranges():
    lumisections = get_oms_lumisection_ranges(VALID_RUN_NUMBER)
    assert len(lumisections) > 0


def test_get_joint_lumisection_ranges():
    lumisections = get_joint_lumisection_ranges(VALID_RUN_NUMBER, VALID_DATASET_NAME)
    assert len(lumisections) > 0


def test_get_collisions18():
    runs = get_runs(filter={"class": "Collisions18"})
    assert len(runs) > 0


def test_get_or_run():
    runs = get_runs(filter={"run_number": {"or": [VALID_RUN_NUMBER]}})


def test_get_datasets_with_filter():
    datasets = get_datasets(
        filter={
            "run_number": {
                "and": [{">": VALID_RUN_RANGE_START}, {"<": VALID_RUN_RANGE_STOP}]
            },
            "tracker-strip": "GOOD",
        }
    )
    assert len(datasets) > 0


def test_generate_json():
    # https://docs.python.org/3/library/warnings.html#testing-warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        generate_json(
            """
{
    "and": [
        {
            "or": [
                {
                    "==": [
                        {
                            "var": "dataset.name"
                        },
                        "/PromptReco/Collisions2018A/DQM"
                    ]
                }
            ]
        }
    ]
}
        """
        )
        assert len(w) == 1
        assert issubclass(w[-1].category, PendingDeprecationWarning)
        assert "deprecated" in str(w[-1].message)


# UNSAFE:
# def test_generate_json():
#     json_logic = """
#         {
#         "and": [
#             {
#                 "or": [
#                     {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018A/DQM"]},
#                     {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018B/DQM"]},
#                     {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018C/DQM"]},
#                     {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018D/DQM"]},
#                     {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018E/DQM"]},
#                     {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018F/DQM"]},
#                     {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018G/DQM"]},
#                     {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018H/DQM"]},
#                     {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018I/DQM"]}
#                 ]
#             },
#             { ">=": [{ "var": "run.oms.energy" }, 6000] },
#             { "<=": [{ "var": "run.oms.energy" }, 7000] },
#             { ">=": [{ "var": "run.oms.b_field" }, 3.7] },
#             { "in": [ "25ns", { "var": "run.oms.injection_scheme" }] },
#             { "==": [{ "in": [ "WMass", { "var": "run.oms.hlt_key" }] }, false] },

#             { "==": [{ "var": "lumisection.rr.dt-dt" }, "GOOD"] },
#             { "==": [{ "var": "lumisection.rr.csc-csc" }, "GOOD"] },
#             { "==": [{ "var": "lumisection.rr.l1t-l1tmu" }, "GOOD"] },
#             { "==": [{ "var": "lumisection.rr.l1t-l1tcalo" }, "GOOD"] },
#             { "==": [{ "var": "lumisection.rr.hlt-hlt" }, "GOOD"] },
#             { "==": [{ "var": "lumisection.rr.tracker-pixel" }, "GOOD"] },
#             { "==": [{ "var": "lumisection.rr.tracker-strip" }, "GOOD"] },
#             { "==": [{ "var": "lumisection.rr.tracker-track" }, "GOOD"] },
#             { "==": [{ "var": "lumisection.rr.ecal-ecal" }, "GOOD"] },
#             { "==": [{ "var": "lumisection.rr.ecal-es" }, "GOOD"] },
#             { "==": [{ "var": "lumisection.rr.hcal-hcal" }, "GOOD"] },
#             { "==": [{ "var": "lumisection.rr.muon-muon" }, "GOOD"] },
#             { "==": [{ "var": "lumisection.rr.jetmet-jetmet" }, "GOOD"] },
#             { "==": [{ "var": "lumisection.rr.lumi-lumi" }, "GOOD"] },
#             { "==": [{ "var": "lumisection.rr.dc-lowlumi" }, "BAD"] },

#             { "==": [{ "var": "lumisection.oms.cms_active" }, true] },
#             { "==": [{ "var": "lumisection.oms.bpix_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.fpix_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.tibtid_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.tecm_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.tecp_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.tob_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.ebm_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.ebp_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.eem_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.eep_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.esm_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.esp_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.hbhea_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.hbheb_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.hbhec_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.hf_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.ho_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.dtm_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.dtp_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.dt0_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.cscm_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.cscp_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.rpc_ready" }, true] },
#             { "==": [{ "var": "lumisection.oms.beam1_present" }, true] },
#             { "==": [{ "var": "lumisection.oms.beam2_present" }, true] },
#             { "==": [{ "var": "lumisection.oms.beam1_stable" }, true] },
#             { "==": [{ "var": "lumisection.oms.beam2_stable" }, true] }
#         ]
#     }
#     """
#     UNSAFE:
#     final_json = generate_json(json_logic)
#     assert final_json is not None
#     json_logic2 = {
#         "and": [
#             {
#                 "or": [
#                     {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018A/DQM"]},
#                     {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018B/DQM"]},
#                     {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018C/DQM"]},
#                     {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018D/DQM"]},
#                     {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018E/DQM"]},
#                     {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018F/DQM"]},
#                     {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018G/DQM"]},
#                     {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018H/DQM"]},
#                     {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018I/DQM"]}
#                 ]
#             },
#             { ">=": [{ "var": "run.oms.energy" }, 6000] },
#             { "<=": [{ "var": "run.oms.energy" }, 7000] },
#             { ">=": [{ "var": "run.oms.b_field" }, 3.7] },
#             { "in": [ "25ns", { "var": "run.oms.injection_scheme" }] },
#             { "==": [{ "in": [ "WMass", { "var": "run.oms.hlt_key" }] }, False] },

#             { "==": [{ "var": "lumisection.rr.dt-dt" }, "GOOD"] },
#             { "==": [{ "var": "lumisection.rr.csc-csc" }, "GOOD"] },
#             { "==": [{ "var": "lumisection.rr.l1t-l1tmu" }, "GOOD"] },
#             { "==": [{ "var": "lumisection.rr.l1t-l1tcalo" }, "GOOD"] },
#             { "==": [{ "var": "lumisection.rr.hlt-hlt" }, "GOOD"] },

#             { "==": [{ "var": "lumisection.oms.bpix_ready" }, True] }
#         ]
#     }
#     final_json2 = generate_json(json_logic2)

#     assert final_json2 is not None

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


def test_create_json():
    json = create_json(
        json_logic=json_logic, dataset_name_filter="/PromptReco/Collisions2018A/DQM"
    )
    print(json)


def test_custom_filter():
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
