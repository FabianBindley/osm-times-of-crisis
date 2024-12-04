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
    coordinates GEOGRAPHY(POINT, 4326),   -- Coordinates stored as a geographic point (latitude/longitude in WGS84)
    uid BIGINT                           -- UID of user who made change
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
WHERE disaster_id = 1
LIMIT 10;


SELECT 
    id, 
    element_id, 
    element_type, 
    edit_type, 
    disaster_id, 
    ST_X(coordinates::geometry) AS longitude, 
    ST_Y(coordinates::geometry) AS latitude, 
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

