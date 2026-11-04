SELECT name, city, overall_rating
FROM hospitals
WHERE state = 'ME' AND overall_rating = 5
ORDER BY name;

SELECT h.name, h.city, h.hospital_type, f.description AS reason
FROM hospitals h
LEFT JOIN footnotes f ON f.code = ANY (h.overall_rating_footnotes)
WHERE h.state = 'ME' AND h.overall_rating IS NULL
ORDER BY h.name;
