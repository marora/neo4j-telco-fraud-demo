// Goal: Identify top callers generating traffic to premium destinations (IRSF pattern)
// Context: Fraudsters generate artificial traffic to high-cost premium-rate numbers (e.g., +882, +979, +44-9xxx).
// Carriers are left with inflated bills — a hallmark of International Revenue Share Fraud.
//
// SQL Way:
// SELECT caller, callee, COUNT(*) AS call_volume, SUM(cost) AS total_cost
// FROM cdrs
// WHERE callee_country = 'PREMIUM'
// GROUP BY caller, callee
// ORDER BY total_cost DESC
// LIMIT 20;
//
// Neo4j Way:
MATCH (n:PhoneNumber)-[c:CALLS]->(p:PhoneNumber)
WHERE c.callee_country = "PREMIUM"
RETURN n.number AS caller,
       p.number AS premiumNumber,
       count(c) AS callVolume,
       sum(c.cost) AS totalCost
ORDER BY totalCost DESC
LIMIT 10;
