SELECT DISTINCT
barcode,
COUNT(barcode) c
FROM scanevent s
LEFT OUTER JOIN drink d ON d.ean = s.barcode
WHERE d.name is null
GROUP BY d.ean, barcode
ORDER BY c
;
