SELECT name, city, overall_rating
FROM hospitals
WHERE state = 'ME' AND overall_rating = 5
ORDER BY name;

SELECT h.name, h.city, h.hospital_type, f.description AS reason
FROM hospitals h
LEFT JOIN footnotes f ON f.code = ANY (h.overall_rating_footnotes)
WHERE h.state = 'ME' AND h.overall_rating IS NULL
ORDER BY h.name;

/* 
As a Maine resident looking for hospital care, 
I want to find hospitals with a 5-star overall rating and understand why some hospitals do not have ratings, 
so that I can make an informed decision about where to receive care.

Done when: The database returns Maine hospitals with a 5-star rating and separately lists unrated Maine 
hospitals with their available CMS footnote explanations.
*/