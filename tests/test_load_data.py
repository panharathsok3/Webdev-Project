from datetime import date
from decimal import Decimal

import pytest

from load_data import (
    SCHEMA_PATH,
    TABLES,
    clean_comparison,
    clean_text,
    hospital_row,
    parse_date,
    parse_flag,
    parse_footnotes,
    parse_integer,
    parse_number,
    patient_survey_row,
)


def test_clean_text_collapses_extra_spaces():
    assert clean_text("RUMFORD  HOSPITAL ") == "RUMFORD HOSPITAL"


@pytest.mark.parametrize("value", ["", "Not Available", "Not Applicable"])
def test_clean_text_turns_missing_markers_into_none(value):
    assert clean_text(value) is None


def test_clean_comparison_merges_case_variants():
    assert clean_comparison("Number of Cases Too Small") == "Number of cases too small"
    assert clean_comparison("Number of cases too small") == "Number of cases too small"
    assert clean_comparison("Not Available") is None


def test_parse_number_keeps_exact_decimals():
    assert parse_number("0.071") == Decimal("0.071")
    assert parse_number("-2.6") == Decimal("-2.6")
    assert parse_number("Not Available") is None


def test_parse_number_rejects_unexpected_text():
    with pytest.raises(ValueError):
        parse_number("about 5")


def test_parse_integer_rejects_fractions():
    assert parse_integer("4") == 4
    with pytest.raises(ValueError):
        parse_integer("4.5")


def test_parse_footnotes_splits_multiple_codes():
    assert parse_footnotes("16, 23") == ["16", "23"]
    assert parse_footnotes("16") == ["16"]
    assert parse_footnotes("") is None


def test_parse_date_reads_cms_format():
    assert parse_date("10/01/2024") == date(2024, 10, 1)
    assert parse_date("") is None


def test_parse_flag():
    assert parse_flag("Yes") is True
    assert parse_flag("Y") is True
    assert parse_flag("No") is False
    assert parse_flag("") is False


def general_info(**overrides):
    row = {
        "Facility ID": "200037",
        "Facility Name": "NORTHERN LIGHT EASTERN MAINE MEDICAL CENTER",
        "Address": "489 STATE STREET",
        "City/Town": "BANGOR",
        "State": "ME",
        "ZIP Code": "04401",
        "County/Parish": "PENOBSCOT",
        "Telephone Number": "(207) 973-7000",
        "Hospital Type": "Acute Care Hospitals",
        "Hospital Ownership": "Voluntary non-profit - Private",
        "Emergency Services": "Yes",
        "Meets criteria for birthing friendly designation": "Y",
        "Hospital overall rating": "5",
        "Hospital overall rating footnote": "",
    }
    row.update(overrides)
    return row


def test_hospital_row_with_rating():
    row = hospital_row(general_info())
    assert row[0] == "200037"
    assert row[5] == "04401"
    assert row[10:] == (True, True, 5, None)


def test_hospital_row_without_rating_keeps_reason():
    row = hospital_row(general_info(**{
        "Hospital overall rating": "Not Available",
        "Hospital overall rating footnote": "16",
    }))
    assert row[12:] == (None, ["16"])


def test_patient_survey_row_treats_not_applicable_as_none():
    row = patient_survey_row({
        "Facility ID": "010001",
        "HCAHPS Measure ID": "H_COMP_1_A_P",
        "HCAHPS Question": 'Patients who reported that their nurses "Always" communicated well',
        "HCAHPS Answer Description": 'Nurses "always" communicated well',
        "Patient Survey Star Rating": "Not Applicable",
        "Patient Survey Star Rating Footnote": "",
        "HCAHPS Answer Percent": "76",
        "HCAHPS Answer Percent Footnote": "",
        "HCAHPS Linear Mean Value": "Not Applicable",
        "Number of Completed Surveys": "1392",
        "Number of Completed Surveys Footnote": "",
        "Survey Response Rate Percent": "17",
        "Survey Response Rate Percent Footnote": "",
        "Start Date": "10/01/2024",
        "End Date": "09/30/2025",
    })
    assert row[4] is None
    assert row[6] == Decimal("76")
    assert row[8] is None
    assert row[9] == 1392


@pytest.mark.parametrize("table_name", [table[0] for table in TABLES])
def test_schema_enables_row_level_security(table_name):
    schema = SCHEMA_PATH.read_text()
    assert f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;" in schema
