SELECT DISTINCT
  coalesce(x1.user_id, x2.user_id, lu."ldapId") as user_id,
  lu.name,
  round(coalesce(x2.smm, 0), 2) - x1.cnt AS kontostand,
  x2.cnt as num_aufladung,
  round(x2.avgAmount, 2) as avg_aufladungssumme,
  round(x2.sumAmount, 2) as total_aufladung
FROM "ldapUsers" lu

  RIGHT OUTER JOIN (
              SELECT
                user_id,
                count(*) AS cnt
              FROM scanevent
              GROUP BY user_id
            ) x1 ON x1.user_id = lu."ldapId"

  RIGHT OUTER JOIN (
              SELECT
                user_id,
                sum(amount) AS smm,
                count(*)    AS cnt,
                avg(amount) AS avgAmount,
                sum(amount) AS sumAmount
              FROM rechargeevent
              GROUP BY user_id
            ) x2 ON x1.user_id = x2.user_id
                    AND x2.user_id = lu."ldapId"

ORDER BY kontostand;
