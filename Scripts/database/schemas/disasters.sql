CREATE TABLE disasters (
    id INTEGER PRIMARY KEY,                             -- Unique identifier for each disaster
    country VARCHAR(50)[],                      -- Country(s) Where the disaster took place
    area VARCHAR(50)[],                         -- Area(s) within a country where the disaster took place
    area_geometry GEOMETRY(MULTIPOLYGON, 4326), -- Multipolygon to store geometry of area(s) under investigation
    date TIMESTAMP                              -- Date of the disaster
);

-- To Query the disasters
SELECT 
    id, 
    country, 
    area, 
    LEFT(ST_AsText(area_geometry), 100) || '...' AS truncated_geometry, 
    date 
FROM disasters 
ORDER BY id;

-- Join the disasters and their changes
SELECT 
    c.id AS change_id,
    c.edit_type,
    c.timestamp AS timestamp, -- Replace with your timestamp column name in changes
    d.id AS disaster_id,
    d.country,
    d.area,
    d.date AS disaster_date
FROM changes c
JOIN disasters d ON c.disaster_id = d.id LIMIT 1000;