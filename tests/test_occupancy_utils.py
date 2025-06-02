import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import datetime
from OccupancyScripts.OCCUPANCY_AM_Model_Extract import (
    extract_property_name,
    parse_month_headers,
    parse_numeric_row,
    parse_percentage_row,
)


def test_extract_property_name():
    assert extract_property_name("Building_01.xlsx") == "Building"
    # The function stops at the first '-' or '_' character
    assert extract_property_name("A-Building Report.xls") == "A"


def test_parse_month_headers():
    header = ["Jan-2022", "Feb-2022", "NotADate"]
    result = parse_month_headers(header)
    assert result[0] == datetime.date(2022, 1, 1)
    assert result[1] == datetime.date(2022, 2, 1)
    assert result[2] is None


def test_parse_numeric_row():
    row = ["1,000", "2", None]
    parsed = parse_numeric_row(row)
    assert parsed[0] == 1000.0
    assert parsed[1] == 2.0
    assert parsed[2] != parsed[2]  # NaN check


def test_parse_percentage_row():
    row = ["50%", "1,000", None]
    parsed = parse_percentage_row(row)
    assert parsed[0] == 0.5
    # Second value is not a percentage so it becomes NaN
    assert parsed[1] != parsed[1]
    assert parsed[2] != parsed[2]  # NaN check
