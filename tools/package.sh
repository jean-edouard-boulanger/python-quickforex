#!/usr/bin/env bash
set -e
rm -f dist/*
python3 setup.py sdist bdist_wheel
