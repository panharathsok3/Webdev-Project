SELECT
    h.name,
    h.city,
    h.state,
    u.measure_name,
    u.score,
    u.compared_to_national,
    u.number_of_patients,
    u.start_date,
    u.end_date
FROM hospitals h
JOIN unplanned_visits u
    ON h.facility_id = u.facility_id
WHERE h.state = 'CA'
  AND u.measure_id LIKE 'READM%'
ORDER BY h.name, u.measure_name;

/*
As a patient comparing hospitals, I want to see how hospitals in my state perform on 
hospital readmission measures, so that I can make a more informed decision about where to receive treatment.

Done when: The user can search hospitals in a selected state and view their readmission-related 
measure scores and how they compare to national benchmarks.
*/