# Performance testing

Done with [Taurus](https://gettaurus.org/), which should be installed via `poetry install --no-root` (see the top-level README). Right now, there's no CI/CD for these tests, so they're run manually.

## Running the tests

First, in this directory, use the `generate_test_data.py` script to generate the fake endpoints. 1,000 should be enough for load testing, and 10,000 should be enough for spike testing.

Then running `bzt config.yaml` should do it.