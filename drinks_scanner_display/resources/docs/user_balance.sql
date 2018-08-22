SELECT x1.user_id, x2.smm - x1.cnt as total
FROM
  (
    SELECT
      user_id,
      count(*) as cnt
    FROM scanevent
    GROUP BY user_id
  ) x1,
  (
    SELECT
      user_id,
      sum(amount) as smm
    FROM rechargeevent
    GROUP BY user_id
  ) x2
  WHERE x1.user_id = x2.user_id
ORDER BY total

