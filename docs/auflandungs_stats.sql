SELECT DISTINCT
  lu."ldapId",
  lu.name,
  coalesce(x2.smm, 0) - x1.cnt AS kontostand,
  x2.cnt as anzahl_aufladungen,
  x2.avgAmount as durchschnittliche_aufladungssummer,
  x2.sumAmount as auflandungssummer_insgesamt
FROM "ldapUsers" lu

  LEFT JOIN (
              SELECT
                user_id,
                count(*) AS cnt
              FROM scanevent
              GROUP BY user_id
            ) x1 ON x1.user_id = lu."ldapId"

  LEFT JOIN (
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