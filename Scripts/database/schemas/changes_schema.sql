CREATE TABLE changes (
    id SERIAL PRIMARY KEY,                -- Unique identifier for each change
    element_id BIGINT NOT NULL,           -- ID of the OSM element (e.g., node, way)
    element_type VARCHAR(10),             -- Node or Way
    edit_type VARCHAR(10),                -- Type of edit (e.g., 'create', 'edit', 'delete')
    timestamp TIMESTAMP,                  -- Timestamp of the edit
    disaster_id INTEGER,                  -- Foreign key to the disasters table, placed after timestamp
    version INTEGER,                      -- Version number of the OSM element
    visible BOOLEAN,                      -- Whether the element is visible
    changeset BIGINT,                     -- Changeset ID associated with the edit
    tags JSONB,                           -- JSONB field for storing tags (e.g., key-value pairs)
    building BOOLEAN,                     -- Boolean flag for building information
    highway BOOLEAN,                      -- Boolean flag for highway information
    coordinates GEOMETRY(POINT, 4326),   -- Coordinates stored as a geometric point (latitude/longitude in WGS84)
    uid BIGINT,                           -- UID of user who made change
    geojson_verified BOOLEAN DEFAULT FALSE -- Indicates whether the GeoJSON has been verified
);



SELECT 
    id, 
    element_id, 
    element_type, 
    edit_type, 
    timestamp, 
    disaster_id, 
    version, 
    visible, 
    changeset, 
    tags, 
    building, 
    highway, 
    ST_X(coordinates::geometry) AS longitude, 
    ST_Y(coordinates::geometry) AS latitude, 
    uid
FROM changes
WHERE disaster_id = 1 AND element_id='4097446'
LIMIT 10;


SELECT 
    id, 
    element_id, 
    element_type, 
    edit_type, 
    disaster_id, 
    tags
    uid
FROM changes
WHERE disaster_id = 1
LIMIT 10;


SELECT 
    id,
    element_id,
    version,
    ROW_NUMBER() OVER (PARTITION BY element_id, version ORDER BY id) AS row_number
FROM changes;

-- Bulk Import detection
SELECT 
    changeset, 
    uid, 
    COUNT(*) AS changes_count
FROM 
    changes
GROUP BY 
    changeset, uid
HAVING 
    COUNT(*) > 1000
ORDER BY 
    changes_count DESC;

CREATE TABLE emilia_romagna_bumb_changes (
    id SERIAL PRIMARY KEY,                -- Unique identifier for each change
    element_id BIGINT NOT NULL,           -- ID of the OSM element (e.g., node, way)
    element_type VARCHAR(10),             -- Node or Way
    edit_type VARCHAR(10),                -- Type of edit (e.g., 'create', 'edit', 'delete')
    timestamp TIMESTAMP,                  -- Timestamp of the edit
    disaster_id INTEGER,                  -- Foreign key to the disasters table, placed after timestamp
    version INTEGER,                      -- Version number of the OSM element
    visible BOOLEAN,                      -- Whether the element is visible
    changeset BIGINT,                     -- Changeset ID associated with the edit
    tags JSONB,                           -- JSONB field for storing tags (e.g., key-value pairs)
    building BOOLEAN,                     -- Boolean flag for building information
    highway BOOLEAN,                      -- Boolean flag for highway information
    coordinates GEOMETRY(POINT, 4326),   -- Coordinates stored as a geographic point (latitude/longitude in WGS84)
    uid BIGINT                           -- UID of user who made change
);

SELECT COUNT(*)
FROM changes
WHERE tags IS NOT NULL   AND jsonb_array_length(tags) > 0;


-- Delete duplicates
WITH CTE AS (
    SELECT 
        id, -- Primary key or unique column for identifying rows
        ROW_NUMBER() OVER (
            PARTITION BY element_id, element_type, version 
            ORDER BY id
        ) AS row_num
    FROM changes
)
DELETE FROM changes_3_year_pre
WHERE id IN (
    SELECT id
    FROM CTE
    WHERE row_num > 1
);

-- Get info on changes within a date range
SELECT  id, 
    element_id, 
    element_type, 
    edit_type, 
    disaster_id, 
    timestamp,
    uid,
    tags 
FROM changes WHERE disaster_id = 14 AND timestamp > '2021-10-01' AND timestamp < '2021-12-01' LIMIT 50000;