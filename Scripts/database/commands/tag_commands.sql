SELECT COUNT(*)
FROM changes
WHERE tags = '{}'::jsonb;

SELECT key, COUNT(*) AS usage_count
FROM (
    SELECT jsonb_object_keys(tags) AS key
    FROM changes
    WHERE tags IS NOT NULL
) subquery
GROUP BY key
ORDER BY usage_count DESC, key;


SELECT COUNT(*) FROM changes WHERE tags ? 'idp:source_20150427' ;

SELECT DISTINCT tags
FROM changes
WHERE tags::jsonb ? 'ref'
LIMIT 10;

--  Count of changes that contain the building key
SELECT COUNT(*)
FROM changes
WHERE tags ? 'building';

-- changes that contain both amenity and building
SELECT element_id, tags
FROM changes
WHERE tags ?& ARRAY['building', 'amenity'] AND disaster_id != 1 LIMIT 10;

-- changes that contain both amenity and building
SELECT element_id, tags
FROM changes
WHERE tags ?& ARRAY['amenity'] AND disaster_id != 1 LIMIT 10;


SELECT 
    element_type, 
    edit_type, 
    disaster_id, 
    version, 
    tags
FROM changes
WHERE tags @> '{"leisure": "common"}';

SELECT 
    COUNT(*)
FROM changes
WHERE tags @> '{"leisure": "common", "emergency:helipad": "potential"}' AND tags @> '{"leisure": "common"}' AND disaster_id = 6;
