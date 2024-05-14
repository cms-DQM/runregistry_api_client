![Build Status](https://github.com/cms-DQM/runregistry_api_client/actions/workflows/test_package.yaml/badge.svg)

# Run Registry Client

Python client to retrieve and query data from [CMS Run Registry](https://cmsrunregistry.web.cern.ch).

To switch to [Dev CMS Run Registry](https://dev-cmsrunregistry.web.cern.ch) do:

```python
import runregistry
runregistry.setup("development")
```

Possible values are `"production"`, `"development"` (will use the development deployment as target), `"qa"` (will use the new SSO proxy on the production deployment) or `"local"` (if you have a local instance of Run Registry's backend running).

## Python version and Virtual env

Python version>=3.6 is required for this package.
A virtual environment is also required, if you are in lxplus you should run the following commands:

```bash
virtualenv -p $(which python3) venv
source venv/bin/activate
```

## Installation

```bash
pip install runregistry
```

## Authentication Prerequisites

> **Warning**
> Grid certificates have been deprecated by CERN. As of version `1.0.0`, the `runregistry`
> client only works with a client ID and a secret.

You will need to create an SSO registration for your application which is going to be using the runregistry API client.

Instructions on how to do it can be found on the [`cernrequests`](https://github.com/CMSTrackerDPG/cernrequests) GitHub page.

Once you have a client ID and a secret, you will need to store them in a file named `.env`. A [sample file](.env_sample) is provided so that you can edit it and rename it to `.env`.

Alternatively, you can run `export SSO_CLIENT_ID=...` and `export SSO_CLIENT_SECRET=...` on the same terminal that you will be running your python script in.

## Usage

### Get a single run (get_run)

```python
import runregistry
run = runregistry.get_run(run_number=328762)
```

### Query several runs (get_runs)

```python
import runregistry
runs = runregistry.get_runs(filter={
   'run_number':{
      'or': [328762, 323555, 323444]
    }
})
```

Apply a custom filter (run_numbers between 309000 and 310000 which had at least one GOOD dt lumisection)

```python
import runregistry
runs = runregistry.get_runs(
    filter={
        'run_number': {
            'and':[
                {'>': 309000},
                {'<': 310000}
            ]
        },
        'dt-dt': 'GOOD'
    }
)
```

Do note that we use `dt-dt` ('dt' twice) this is due to the fact that there are multiple workspaces, the first 'dt' states we are in dt workspace, the second 'dt' states we want column 'dt'. So the syntax for status flags is `{workspace}-{column}`. If we wanted runs with the strip column from tracker workspace to have at least 1 lumisection GOOD, the query would look like this:

```python
import runregistry
runs = runregistry.get_runs(
    filter={
        'run_number': {
            'and':[
                {'>': 309000},
                {'<': 310000}
            ]
        },
        'tracker-strip': 'GOOD'
    }
)
```

Depending on the attribute you can use different operators:

#### Operators

| Attribute |       Supported operators       |
| --------- | :-----------------------------: |
| number    | '=', '>', '<', '>=', '<=', '<>' |
| String    |        =, like, notlike         |
| Boolean   |         = (true, false)         |
| date      | '=', '>', '<', '>=', '<=', '<>' |

When using `like` or `notlike` operator, you must surround your query with percentage signs, see example below.

When filtering for triplet attributes (anything that is GOOD/BAD/STANDBY...) you must not use any String values, the only value allowed is strict equality '=' and is set by default. The values allowed are GOOD, BAD, STANDBY, NOTSET, EXCLUDED and EMPTY.

You can combine the filters as well:

```python
import runregistry
runs = runregistry.get_runs(
    filter={
        'run_number': {
            'and':[
                {'>': 309000},
                {'<': 310000}
            ]
        },
        'hlt_key': {
            'like': '%commissioning2018%'
        }
        'significant': {
            '=': True
        }
    }
)
```

If by observing the Network Requests in RR web application, you want to use the same filters observed by the network request. Just passs `ignore_filter_transformation=True` to any query.

Example (run_numbers between 309000 and 310000 which had at least one GOOD dt lumisection):

```python
import runregistry
runs = runregistry.get_runs(
    filter={
        'run_number': {
            'and':[
                {'>': 309000},
                {'<': 310000}
            ]
        },
        # Remember! this will only work if you pass ignore_filter_transformation=True (please read above what this means), otherwise use the other examples
        'oms_attributes.hlt_key': {
            'like': '%commissioning2018%'
        },
        'triplet_summary.dt-dt.GOOD': {
            '>': 0
        }
    },
    ignore_filter_transformation=True
)
```

Also, if by observing the Network Requests in RR web application, you want to obtain the data as it is seen in the network requests. Just `compress_attributes=False`, for example:

```python
import runregistry
runs = runregistry.get_runs(
    filter={
        'run_number': {
            'and':[
                {'>': 309000},
                {'<': 310000}
            ]
        },
        'dt': 'GOOD'
    },
    compress_attributes=False
)
```

querying by comments and cause is not yet possible

### Get dataset

```python
import runregistry
dataset = runregistry.get_dataset(
        run_number=327604,
        dataset_name="/PromptReco/HICosmics18A/DQM"
    )
```

### Get datasets

```python
import runregistry
datasets = runregistry.get_datasets(
    filter={
        'run_number': {
            'and':[
                {'>': 309000},
                {'<': 310000}
            ]
        }
    }
)
```

### Get Lumisections

#### Get the array of lumisections

You can query the lumisections of a run (or dataset), you will need the run number and the dataset name (when querying for a run, the dataset name must be 'online')

```python
import runregistry
# lumisections = runregistry.get_lumisections(run_number, dataset_name)
lumisections = runregistry.get_lumisections(327743, "/PromptReco/HICosmics18A/DQM")
```

The response will be an array of lumisections which will contain `{workspace}-{column}: {"status":"Either GOOD/BAD/STANDBY...", "comment": "a comment made for the range", "cause":"a common repeated cause"}`

To get OMS data: use the OMS API. You should only use Run Registry for data that RR is responsible for.
However if you still want to access OMS lumisections, you can do so like this:

Previous Run Registry allowed you to change OMS (in that time WBM) attributes per dataset, if you need certain dataset lumisections you can provide the name of the RR dataset in the second argument:

```python
import runregistry
# oms_lumisections = runregistry.get_oms_lumisections(run_number, dataset_name)
oms_lumisections = get_oms_lumisections(327743, 'online')
# If you want to get particular dataset that is not online for OMS lumisections:
dataset_oms_lumisections = get_oms_lumisections(327743, '/PromptReco/HICosmics18A/DQM')
```

#### Get lumisection ranges

Usually there will be runs/datasets which contain an enormous amount of lumisections (some even more than 5000), therefore it can be heavy on the API to query for these type of lumisections.

A query to retrieve ranges is also possible, you can do it like this:

```python
import runregistry
# lumisections = runregistry.get_lumisection_ranges(run_number, dataset_name)
lumisections = runregistry.get_lumisection_ranges(327743, "/PromptReco/HICosmics18A/DQM")
```

You will receive an array of ranges, that apart from stating the triplets (comment, status and cause) for each column, the array will consist of two more attributes called **start** (lumisection where range starts) and **end** (lumisection where range ends).

### Handling the response

When filtering runs, the attributes from the response get divided into those belonging to OMS and those belonging to RR (to see which belong to which, see the tables below, or go through a response).

Those that belong to OMS are inside "oms_attributes".

Those that belong to RR are inside "rr_attributes".

### Attributes available to query

According to the type of attribute (number, string, boolean), see the Operator table above to see which types of operators can be applied to querying

Oms Attributes:

| Attribute                                                                                  |  Type   | Belongs to |
| ------------------------------------------------------------------------------------------ | :-----: | :--------: |
| run_number                                                                                 | number  |    OMS     |
| energy                                                                                     | number  |    OMS     |
| l1_key                                                                                     | string  |    OMS     |
| b_field                                                                                    | number  |    OMS     |
| hlt_key                                                                                    | string  |    OMS     |
| l1_menu                                                                                    | string  |    OMS     |
| l1_rate                                                                                    | number  |    OMS     |
| duration                                                                                   | number  |    OMS     |
| end_lumi                                                                                   | number  |    OMS     |
| end_time                                                                                   |  date   |    OMS     |
| sequence                                                                                   | string  |    OMS     |
| init_lumi                                                                                  | number  |    OMS     |
| clock_type                                                                                 | string  |    OMS     |
| start_time                                                                                 |  date   |    OMS     |
| fill_number                                                                                | number  |    OMS     |
| l1_hlt_mode                                                                                | string  |    OMS     |
| last_update                                                                                |  date   |    OMS     |
| ls_duration                                                                                | number  |    OMS     |
| stable_beam                                                                                | boolean |    OMS     |
| trigger_mode                                                                               | string  |    OMS     |
| cmssw_version                                                                              | string  |    OMS     |
| recorded_lumi                                                                              | number  |    OMS     |
| delivered_lumi                                                                             | number  |    OMS     |
| tier0_transfer                                                                             | boolean |    OMS     |
| l1_key_stripped                                                                            | string  |    OMS     |
| fill_type_party1                                                                           | string  |    OMS     |
| fill_type_party2                                                                           | string  |    OMS     |
| hlt_physics_rate                                                                           | number  |    OMS     |
| hlt_physics_size                                                                           | number  |    OMS     |
| fill_type_runtime                                                                          | string  |    OMS     |
| hlt_physics_counter                                                                        | number  |    OMS     |
| l1_triggers_counter                                                                        | number  |    OMS     |
| l1_hlt_mode_stripped                                                                       | string  |    OMS     |
| hlt_physics_throughput                                                                     | number  |    OMS     |
| initial_prescale_index                                                                     | number  |    OMS     |
| beams_present_and_stable                                                                   | boolean |    OMS     |
| es_included                                                                                | boolean |    OMS     |
| hf_included                                                                                | boolean |    OMS     |
| daq_included                                                                               | boolean |    OMS     |
| dcs_included                                                                               | boolean |    OMS     |
| dqm_included                                                                               | boolean |    OMS     |
| gem_included                                                                               | boolean |    OMS     |
| trg_included                                                                               | boolean |    OMS     |
| hcal_included                                                                              | boolean |    OMS     |
| tcds_included                                                                              | boolean |    OMS     |
| pixel_included                                                                             | boolean |    OMS     |
| tracker_included                                                                           | boolean |    OMS     |
| \*\_included (be sure to add it to the validation runregistry/attributes if it's not here) | boolean |    OMS     |

RR Run Attributes:

| Attribute   |  Type   | Belongs to |
| ----------- | :-----: | :--------: |
| class       | string  |     RR     |
| state       | string  |     RR     |
| significant | boolean |     RR     |
| stop_reason | string  |     RR     |

RR Dataset Attributes:

| Attribute     |  Type  | Belongs to |
| ------------- | :----: | :--------: |
| dataset_name  | string |     RR     |
| dt_state      | string |     RR     |
| csc_state     | string |     RR     |
| hlt_state     | string |     RR     |
| l1t_state     | string |     RR     |
| rpc_state     | string |     RR     |
| tau_state     | string |     RR     |
| btag_state    | string |     RR     |
| ecal_state    | string |     RR     |
| hcal_state    | string |     RR     |
| lumi_state    | string |     RR     |
| muon_state    | string |     RR     |
| ctpps_state   | string |     RR     |
| castor_state  | string |     RR     |
| egamma_state  | string |     RR     |
| global_state  | string |     RR     |
| jetmet_state  | string |     RR     |
| tracker_state | string |     RR     |

The dt_state, csc_state and so on, are the workspace OFFLINE states of the datasets, they can be either OPEN, SIGNOFF or COMPLETED.

For Offline and Online status flags, filtering is also available. The Attribute is composed by `{workspace}-{column}`. So for example if we want to query for GOOD tracker-strip datasets of runs between 309000 and 310000, we would do it like this:

```python
import runregistry
datasets = runregistry.get_datasets(filter={
    'tracker-strip':'GOOD'
    'run_number': {'and': [{'>': 309000}, {'<': 310000}]},
})
```

## Generating JSONs

In order to generate JSONs (like the golden json) you must send the configuration of the attributes you wish the generated json to satisfy (in json-logic)

The json logic below generates a json file for the dataset name: "/PromptReco/Collisions2018A/DQM" although you can use placeholders just as in the json portal as: /PromptReco/Collisions2018(A|B)/DQM or /PromptReco/Collisions2018\_/DQM the underscore '\_' is a wildcard.

```python
import runregistry
json_logic = {
  "and": [
      { ">=": [{ "var": "run.oms.energy" }, 6000] },
      { "<=": [{ "var": "run.oms.energy" }, 7000] },
      { ">=": [{ "var": "run.oms.b_field" }, 3.7] },
      { "in": [ "25ns", { "var": "run.oms.injection_scheme" }] },
      { "==": [{ "in": [ "WMass", { "var": "run.oms.hlt_key" }] }, False] },

      { "==": [{ "var": "lumisection.rr.dt-dt" }, "GOOD"] },
      { "==": [{ "var": "lumisection.rr.csc-csc" }, "GOOD"] },
      { "==": [{ "var": "lumisection.rr.l1t-l1tmu" }, "GOOD"] },
      { "==": [{ "var": "lumisection.rr.l1t-l1tcalo" }, "GOOD"] },
      { "==": [{ "var": "lumisection.rr.hlt-hlt" }, "GOOD"] },

      { "==": [{ "var": "lumisection.oms.bpix_ready" }, True] }
  ]
}
generated_json = runregistry.create_json(json_logic=json_logic, dataset_name_filter="/PromptReco/Collisions2018A/DQM")
```

### Advanced

You can also manipulate runs via API:

1. Mark run significant:
    ```python
    runregistry.make_significant_runs(run=362761)
    ```
2. Reset RR attributes and reload data from OMS:
    ```python
    runregistry.reset_RR_attributes_and_refresh_runs(run=362761)
    ```
3. Move runs from one state to another:
    ```python
    runregistry.move_runs("OPEN", "SIGNOFF", run=362761)
    ```

## Troubleshooting

### Support

If you have any questions, or the client is not working properly feel free to drop our team an email at [cms-dqm-coreTeam@cern.ch](mailto:cms-dqm-coreTeam@cern.ch).

### [Package developers] Updating the package on PyPI

```bash
python3 -m pip install --upgrade pip build twine
python3 -m build
python3 -m twine upload --skip-existing --repository pypi dist/*
```
Instructions from [here](https://packaging.python.org/en/latest/tutorials/packaging-projects/).

## Running the tests

### Locally

You will be needing a file named `.env` with the following variables:

```bash
SSO_CLIENT_ID=<change>
SSO_CLIENT_SECRET=<change>
ENVIRONMENT=development
```

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r testing-requirements.txt
pip install -e .
pytest tests -s
```

### GitHub actions

Automated GitHub actions run on each push to the repository. The workflow is defined [here](./.github/workflows/test_package.yaml)

The same env variables are needed as in [local testing](#locally), so those are added [here](https://github.com/cms-DQM/runregistry_api_client/settings/secrets/actions).

## FAQ

### Does this work with Python 2.7?

No.

### Should I be using `runregistry_api_client` for getting OMS data?

No*.

Our recommendation is to query Run Registry only for data that RR is responsible for.

<small>*It's not that you can't, it's just that this puts extra burden on the application, making it slow for everyone.</small>

### Is the token stored somewhere and reused?

No, almost every function call gets a new token. This is not ideal, and it may be improved in the future.