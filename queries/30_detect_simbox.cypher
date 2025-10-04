// Detect SIM Box fraud: devices used by 50+ numbers
MATCH (d:Device)<-[:USES]-(n:PhoneNumber)
WITH d, count(DISTINCT n) AS numberCount
WHERE numberCount >= 50
RETURN d.imei AS suspiciousDevice, numberCount
ORDER BY numberCount DESC
LIMIT 20;
