// Detect IRSF: traffic spikes to premium destinations in last 1 hour
MATCH (n:PhoneNumber)-[c:CALLS]->(p:PhoneNumber)
WHERE p.callee_country = "PREMIUM"
  AND c.ts > timestamp() - 3600000
RETURN n.number AS caller, p.number AS premiumNumber,
       count(c) AS callVolume, sum(c.cost) AS totalCost
ORDER BY totalCost DESC
LIMIT 20;

