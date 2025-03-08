-- The SQL query groups user search queries into N evenly distributed groups using a hash function.
-- I used N = 1000 for this task
-- For each query, it finds related queries that appear in the same user sessions and removes duplicates.
-- The results are then aggregated into an array of structures, each containing a query and its related queries.
-- This approach ensures efficient data storage and retrieval, improves performance, and allows for effective caching.
-- By using hashing, we balance the load across groups, making the system scalable and cost-effective
SELECT
  group_id,
  ARRAY_AGG(STRUCT(query, related_queries)) AS queries
FROM (
  SELECT
    MOD(ABS(FARM_FINGERPRINT(query)), 1000) AS group_id,
    query,
    ARRAY_AGG(related_query ORDER BY count DESC LIMIT 3) AS related_queries
  FROM (
    SELECT a.query AS query, b.query AS related_query, COUNT(*) AS count
    FROM `charged-state-451616-h7.query_logs_dataset.query_logs` a
    JOIN `charged-state-451616-h7.query_logs_dataset.query_logs` b
    ON a.session = b.session AND a.query != b.query
    WHERE a.query IS NOT NULL AND a.query != ''
      AND b.query IS NOT NULL AND b.query != ''
    GROUP BY a.query, b.query
  )
  GROUP BY query, group_id
)
GROUP BY group_id