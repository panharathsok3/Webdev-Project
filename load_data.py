import csv
import json
import shutil
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.request import urlopen

from database import engine

METASTORE_URL = "https://data.cms.gov/provider-data/api/1/metastore/schemas/dataset/items/{}"
PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data"
SCHEMA_PATH = PROJECT_DIR / "schema.sql"

MISSING_VALUES = {"", "Not Available", "Not Applicable"}


def clean_text(value):
    value = " ".join(value.split())
    if value in MISSING_VALUES:
        return None
    return value


def clean_comparison(value):
    value = clean_text(value)
    if value is None:
        return None
    return value.capitalize()


def parse_number(value):
    value = clean_text(value)
    if value is None:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        raise ValueError(f"Not a number: {value!r}")


def parse_integer(value):
    number = parse_number(value)
    if number is None:
        return None
    if number != number.to_integral_value():
        raise ValueError(f"Not a whole number: {value!r}")
    return int(number)


def parse_footnotes(value):
    codes = [code.strip() for code in value.split(",") if code.strip()]
    return codes or None


def parse_date(value):
    value = clean_text(value)
    if value is None:
        return None
    return datetime.strptime(value, "%m/%d/%Y").date()


def parse_flag(value):
    return clean_text(value) in ("Yes", "Y")


def hospital_row(row):
    return (
        row["Facility ID"],
        clean_text(row["Facility Name"]),
        clean_text(row["Address"]),
        clean_text(row["City/Town"]),
        row["State"],
        clean_text(row["ZIP Code"]),
        clean_text(row["County/Parish"]),
        clean_text(row["Telephone Number"]),
        clean_text(row["Hospital Type"]),
        clean_text(row["Hospital Ownership"]),
        parse_flag(row["Emergency Services"]),
        parse_flag(row["Meets criteria for birthing friendly designation"]),
        parse_integer(row["Hospital overall rating"]),
        parse_footnotes(row["Hospital overall rating footnote"]),
    )


def footnote_row(row):
    return (row["Footnote"].strip(), clean_text(row["Footnote Text"]))


def infection_row(row):
    return (
        row["Facility ID"],
        row["Measure ID"],
        clean_text(row["Measure Name"]),
        clean_comparison(row["Compared to National"]),
        parse_number(row["Score"]),
        parse_footnotes(row["Footnote"]),
        parse_date(row["Start Date"]),
        parse_date(row["End Date"]),
    )


def unplanned_visit_row(row):
    return (
        row["Facility ID"],
        row["Measure ID"],
        clean_text(row["Measure Name"]),
        clean_comparison(row["Compared to National"]),
        parse_number(row["Denominator"]),
        parse_number(row["Score"]),
        parse_number(row["Lower Estimate"]),
        parse_number(row["Higher Estimate"]),
        parse_integer(row["Number of Patients"]),
        parse_integer(row["Number of Patients Returned"]),
        parse_footnotes(row["Footnote"]),
        parse_date(row["Start Date"]),
        parse_date(row["End Date"]),
    )


def patient_survey_row(row):
    return (
        row["Facility ID"],
        row["HCAHPS Measure ID"],
        clean_text(row["HCAHPS Question"]),
        clean_text(row["HCAHPS Answer Description"]),
        parse_integer(row["Patient Survey Star Rating"]),
        parse_footnotes(row["Patient Survey Star Rating Footnote"]),
        parse_number(row["HCAHPS Answer Percent"]),
        parse_footnotes(row["HCAHPS Answer Percent Footnote"]),
        parse_number(row["HCAHPS Linear Mean Value"]),
        parse_integer(row["Number of Completed Surveys"]),
        parse_footnotes(row["Number of Completed Surveys Footnote"]),
        parse_number(row["Survey Response Rate Percent"]),
        parse_footnotes(row["Survey Response Rate Percent Footnote"]),
        parse_date(row["Start Date"]),
        parse_date(row["End Date"]),
    )


TABLES = [
    ("hospitals", "xubh-q36u", hospital_row, [
        "facility_id", "name", "address", "city", "state", "zip_code", "county",
        "phone", "hospital_type", "ownership", "emergency_services",
        "birthing_friendly", "overall_rating", "overall_rating_footnotes",
    ]),
    ("footnotes", "y9us-9xdf", footnote_row, ["code", "description"]),
    ("infections", "77hc-ibv8", infection_row, [
        "facility_id", "measure_id", "measure_name", "compared_to_national",
        "score", "footnotes", "start_date", "end_date",
    ]),
    ("unplanned_visits", "632h-zaca", unplanned_visit_row, [
        "facility_id", "measure_id", "measure_name", "compared_to_national",
        "denominator", "score", "lower_estimate", "higher_estimate",
        "number_of_patients", "number_of_patients_returned", "footnotes",
        "start_date", "end_date",
    ]),
    ("patient_survey", "dgck-syfz", patient_survey_row, [
        "facility_id", "measure_id", "question", "answer_description",
        "star_rating", "star_rating_footnotes", "answer_percent",
        "answer_percent_footnotes", "linear_mean_value", "completed_surveys",
        "completed_surveys_footnotes", "response_rate_percent",
        "response_rate_footnotes", "start_date", "end_date",
    ]),
]


def download_csv(dataset_id, table_name):
    csv_path = DATA_DIR / f"{table_name}.csv"
    if csv_path.exists():
        print(f"Using existing {csv_path.name}")
        return csv_path

    with urlopen(METASTORE_URL.format(dataset_id)) as response:
        metadata = json.load(response)
    download_url = metadata["distribution"][0]["downloadURL"]

    print(f"Downloading {csv_path.name} from {download_url}")
    partial_path = csv_path.with_suffix(".part")
    with urlopen(download_url) as response, open(partial_path, "wb") as file:
        shutil.copyfileobj(response, file)
    partial_path.rename(csv_path)
    return csv_path


def read_rows(csv_path, to_row):
    with open(csv_path, newline="", encoding="utf-8-sig") as file:
        for line_number, row in enumerate(csv.DictReader(file), start=2):
            try:
                yield to_row(row)
            except ValueError as error:
                raise ValueError(f"{csv_path.name} line {line_number}: {error}") from error


def load_all():
    DATA_DIR.mkdir(exist_ok=True)
    csv_paths = {
        table_name: download_csv(dataset_id, table_name)
        for table_name, dataset_id, _, _ in TABLES
    }

    with engine.begin() as connection:
        cursor = connection.connection.driver_connection.cursor()
        cursor.execute(SCHEMA_PATH.read_text())
        for table_name, _, to_row, columns in TABLES:
            copy_sql = f"COPY {table_name} ({', '.join(columns)}) FROM STDIN"
            with cursor.copy(copy_sql) as copy:
                for row in read_rows(csv_paths[table_name], to_row):
                    copy.write_row(row)
            cursor.execute(f"SELECT count(*) FROM {table_name}")
            print(f"Loaded {cursor.fetchone()[0]} rows into {table_name}")


if __name__ == "__main__":
    load_all()
