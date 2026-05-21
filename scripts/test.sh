#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=packages/jarvis-core python3 -m unittest discover -s packages/jarvis-core/tests
