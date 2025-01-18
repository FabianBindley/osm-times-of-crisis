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

