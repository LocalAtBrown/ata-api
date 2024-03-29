# ata-api

<!-- [![Release](https://img.shields.io/github/v/release/localAtBrown/ata-api)](https://img.shields.io/github/v/release/localAtBrown/ata-api) -->
<!-- [![Build status](https://img.shields.io/github/workflow/status/localAtBrown/ata-api/merge-to-main)](https://img.shields.io/github/workflow/status/localAtBrown/ata-api/merge-to-main) -->

[![Python version](https://img.shields.io/badge/python_version-3.9.-blue)](https://github.com/psf/black)
[![Code style with black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/psf/black)
[![More style with flake8](https://img.shields.io/badge/code_style-flake8-blue)](https://flake8.pycqa.org)
[![Imports with isort](https://img.shields.io/badge/%20imports-isort-blue)](https://pycqa.github.io/isort/)
[![Type checking with mypy](https://img.shields.io/badge/type_checker-mypy-blue)](https://mypy.readthedocs.io)
[![License](https://img.shields.io/github/license/localAtBrown/ata-api)](https://img.shields.io/github/license/localAtBrown/ata-api)

API to serve AtA prescriptions.

## Usage

In production, this is deployed via CD on AWS.

To run it locally from the `ata_api` directory, run: `uvicorn main:app --reload`. This will run the API on
`localhost:8000`. You can confirm it is up by pinging the root: `curl localhost:8000/` should return a simple message.
To run it while pointing at a database, from the `ata_api` directory run:
`HOST=fakehost PASSWORD=fakepw DB_NAME=fakedb USERNAME=fakeuser PORT=fakeport uvicorn main:app --reload`

## Development

This project uses [Poetry](https://python-poetry.org/) to manage dependencies. It also helps with pinning dependency and python
versions. We also use [pre-commit](https://pre-commit.com/) with hooks for [isort](https://pycqa.github.io/isort/),
[black](https://github.com/psf/black), and [flake8](https://flake8.pycqa.org/en/latest/) for consistent code style and
readability. Note that this means code that doesn't meet the rules will fail to commit until it is fixed.

We use [mypy](https://mypy.readthedocs.io/en/stable/index.html) for static type checking. This can be run [manually](#run-static-type-checking),
and the CI runs it on PRs to the `main` branch. We also use [pytest](https://docs.pytest.org/en/7.2.x/) to run our tests.
This can be run [manually](#run-tests) and the CI runs it on PRs to the `main` branch.

### Setup

1. [Install Poetry](https://python-poetry.org/docs/#installation).
2. [Install pyenv](https://github.com/pyenv/pyenv)
3. Install the correct Python version for this project, here Python 3.9: `pyenv install 3.9`
4. Activate the installed Python version in the current shell: `pyenv shell 3.9`
5. Create a virtual environment from this Python version using Poetry: `poetry env use 3.9`
6. Activate the virtual environment: `source $(poetry env list --full-path)/bin/activate`
7. Run `poetry install --no-root`
8. Run  `pre-commit install` to set up `pre-commit`

You're all set up! Your local environment should include all dependencies, including dev dependencies like `black`.
This is done with Poetry via the `poetry.lock` file.

The next times you open this directory on your IDE, make sure the virtual environment is activated (i.e., Step 6).

### Run Code Format and Linting

To manually run isort, black, and flake8 all in one go, simply run `pre-commit run --all-files`. Explore the `pre-commit` docs (linked above)
to see more options.

### Run Static Type Checking

To manually run mypy, simply run `mypy` from the root directory of the project. It will use the default configuration
specified in `pyproject.toml`.

### Update Dependencies

To update dependencies in your local environment, make changes to the `pyproject.toml` file then run `poetry update` from the root directory of the project.

### Run Tests

To manually run rests, simply run `pytest tests` from the root directory of the project. Explore the `pytest` docs (linked above)
to see more options.

Integration tests (run via `pytest -m integration` or `pytest tests`, which runs all tests) require a mock database to be set up locally. Provided you've already installed Docker, in a separate terminal:

```bash
docker pull postgres
docker run --rm --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_HOST_AUTH_METHOD=trust -p 127.0.0.1:5432:5432/tcp postgres
```
