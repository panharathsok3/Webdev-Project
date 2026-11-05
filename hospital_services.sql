SELECT
    name,
    city,
    state,
    hospital_type,
    emergency_services,
    birthing_friendly,
    overall_rating
FROM hospitals
WHERE state = 'CA'
  AND emergency_services = TRUE
ORDER BY overall_rating DESC NULLS LAST, name;

/*
As a patient looking for hospital care, I want to find hospitals in my state that offer emergency services 
and compare their overall ratings, so that I can choose a hospital that meets my needs.

Done when: The user can search for hospitals in a selected state that provide emergency services, 
and the results are sorted from highest to lowest overall rating.
*/