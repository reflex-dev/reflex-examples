#!/bin/sh

set -xeuo pipefail

ruff check --fix playground
ruff format playground
pyright playground
