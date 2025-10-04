// Detect Wangiri: many short inbound calls from international numbers
MATCH (a:PhoneNumber)-[c:CALLS]->(b:PhoneNumber)
WHERE c.duration <= 3 AND c.caller_country = "INTL"
RETURN a.number AS suspiciousCaller,
       count(c) AS attempts,
       collect(DISTINCT b.number)[0..10] AS victims
ORDER BY attempts DESC
LIMIT 20;

