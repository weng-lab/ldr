#!/bin/bash
set -e

# cd to project root directory
cd "$(dirname "$(dirname "$0")")"
cd src

# test
python3 -m unittest test.test_utilities
python3 -m unittest test.test_annotations
