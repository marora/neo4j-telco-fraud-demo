// Detect PBX Toll Fraud: bursts of premium calls during off-hours
MATCH (s:Subscriber)-[:OWNS]->(n:PhoneNumber)-[c:CALLS]->(p:PhoneNumber)
WHERE (toInteger(substring(c.start, 11,2)) < 6   // before 6am
   OR toInteger(substring(c.start, 11,2)) > 23) // after 11pm
  AND p.callee_country = "PREMIUM"
WITH s, count(c) AS callCount, sum(c.cost) AS totalCost
WHERE callCount > 20 OR totalCost > 100
RETURN s.name AS subscriber, callCount, totalCost
ORDER BY totalCost DESC
LIMIT 20;
