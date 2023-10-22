# Perpetuator - `perc` - CLI

## Purpose

This CLI is used to interact with the Perpetuator APIs.

## Setup

```shell
pyenv shell 3.10.0
```

If it is your first time using poetry, then install that to the hosts `pyenv` for the current version:
```shell
pip install poetry
```

Now tell poetry what version of python is expected for this project:
```shell
poetry env use 3.10.0
```

## Install

To install dependencies _and_ to install `perc` so that it is linked to the source in this repo run:

```shell
poetry build
poetry install
```

_NOTE: Consider `sudo pip install .` as was seen in `WoeUSB-ng`_

Sets up at: `perpetuator-cli/.venv/bin/perc`

## Publish

To PyPi:

```shell
poetry publish --build
```

## Test

Sequential
```shell
python -m unittest --coverage --coverage-rcfile .coveragerc --coverage-html ./coverage
```

Parallel
```shell
python -m unittest_parallel -s $PWD/tests -t $PWD
```

## Coverage

Sequential
```shell
coverage run -m unittest discover
coverage html
```

Parallel
```shell
PYTHONPATH=${PWD}/site-packages python -m unittest_parallel -s $PWD/tests -t $PWD --coverage --coverage-rcfile .coveragerc --coverage-html ./coverage -p test_collections.py
```


# Usage

```shell
perc -h
```

## Commands
```shell
perc 
perc token
```

## API Command

### Show User Info `GET /user`
Get the current user, derived from the token.
```shell
perc get-user
```

### List Collections `GET /index`
```shell
perc get-index
```

### Upload Document `POST /uploads`
```shell
perc post-uploads-file ./tests/data/Nancy_Nobodyknows.md
perc post-uploads-file ./tests/data/Bob_McSecret.md
``` 

### List Uploads `GET /uploads`
```shell
perc get-uploads
```

### Prompt `POST /index`
Ask questions, notice it doesn't yet know about our documents.
```shell
perc post-index personal "Do you know the story of Bob McSecret?"
perc post-index default "Do you know the story of Bob McSecret?"
```

# Demo
```shell
perc -h
perc post-index default "How many cows does Bob have?"
# API
#perc post-uploads-file ./tests/data/Bob_McSecret.md
#perc post-uploads-file ./tests/data/Nancy_Nobodyknows.md
# S3
perc put-uploads-file ./tests/data/Bob_McSecret.md
perc put-uploads-file ./tests/data/Nancy_Nobodyknows.md
# Re-index, not needed as they are indexed upon upload
#perc post-index-file default Nancy_Nobodyknows.md
#perc post-index-file default Bob_McSecret.md
perc post-index default "How many cows does Bob McSecret have?"
perc post-index default "Do you know the story of Nancy Nobodyknows?"
perc post-index default "How many cows and pigeons do Nancy Nobodyknows and Bob McSecret have?"
perc post-index default "What are the names of Nancy Nobodyknows' pigeons?"
# Record the threadId from the previous command and use it here:
perc get-threads | jq '.[] | select(.threadId == "e555b070-8373-4080-b7b4-8d019c5a9514")'\n
perc get-index default "What similarities are there between Nancy Nobodyknows and Bob McSecret?"
# List uploads
perc get-uploads
# List collections
perc get-index
```
