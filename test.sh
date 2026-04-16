#!/bin/bash
set -e
cd "$(dirname "$0")"
python3 -m pytest tests/test_hr/ tests/test_company_scoping/ -v
