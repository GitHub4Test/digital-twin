#!/usr/bin/env bash
set -euo pipefail

source ./build/.env

cd $1

rm -rf dist build *.egg-info

poetry build

echo "Package built:"
ls -lh dist/