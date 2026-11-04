DROP TABLE IF EXISTS patient_survey, unplanned_visits, infections, footnotes, hospitals;

CREATE TABLE hospitals (
    facility_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    city TEXT,
    state TEXT NOT NULL,
    zip_code TEXT,
    county TEXT,
    phone TEXT,
    hospital_type TEXT,
    ownership TEXT,
    emergency_services BOOLEAN NOT NULL,
    birthing_friendly BOOLEAN NOT NULL,
    overall_rating SMALLINT CHECK (overall_rating BETWEEN 1 AND 5),
    overall_rating_footnotes TEXT[]
);

CREATE TABLE footnotes (
    code TEXT PRIMARY KEY,
    description TEXT NOT NULL
);

CREATE TABLE infections (
    facility_id TEXT NOT NULL REFERENCES hospitals,
    measure_id TEXT NOT NULL,
    measure_name TEXT NOT NULL,
    compared_to_national TEXT,
    score NUMERIC,
    footnotes TEXT[],
    start_date DATE,
    end_date DATE,
    PRIMARY KEY (facility_id, measure_id)
);

CREATE TABLE unplanned_visits (
    facility_id TEXT NOT NULL REFERENCES hospitals,
    measure_id TEXT NOT NULL,
    measure_name TEXT NOT NULL,
    compared_to_national TEXT,
    denominator NUMERIC,
    score NUMERIC,
    lower_estimate NUMERIC,
    higher_estimate NUMERIC,
    number_of_patients INTEGER,
    number_of_patients_returned INTEGER,
    footnotes TEXT[],
    start_date DATE,
    end_date DATE,
    PRIMARY KEY (facility_id, measure_id)
);

CREATE TABLE patient_survey (
    facility_id TEXT NOT NULL REFERENCES hospitals,
    measure_id TEXT NOT NULL,
    question TEXT NOT NULL,
    answer_description TEXT,
    star_rating SMALLINT CHECK (star_rating BETWEEN 1 AND 5),
    star_rating_footnotes TEXT[],
    answer_percent NUMERIC,
    answer_percent_footnotes TEXT[],
    linear_mean_value NUMERIC,
    completed_surveys INTEGER,
    completed_surveys_footnotes TEXT[],
    response_rate_percent NUMERIC,
    response_rate_footnotes TEXT[],
    start_date DATE,
    end_date DATE,
    PRIMARY KEY (facility_id, measure_id)
);
