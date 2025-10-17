// Detect Wangiri: many short inbound calls from international numbers
//
// Who’s making short calls from international numbers?
// SQL Way:
// SELECT 
//    caller AS suspiciousCaller,
//    COUNT(*) AS attempts,
//    ARRAY_AGG(DISTINCT callee) AS victims
// FROM cdrs
// WHERE duration <= 3
//   AND caller_country = 'INTL'
// GROUP BY caller
// ORDER BY attempts DESC
// LIMIT 10;
// 
// Neo4j Way: 
MATCH (a:PhoneNumber)-[c:CALLS]->(b:PhoneNumber)
WHERE c.duration <= 3 AND c.caller_country = "INTL"
RETURN a.number AS suspiciousCaller,
       count(c) AS attempts,
       collect(DISTINCT b.number)[0..10] AS victims
ORDER BY attempts DESC
LIMIT 10;

// It quickly becomes:
// 1. “Are those callers linked by common devices, routes, or geographies?”
// 2. “Are they calling overlapping victim sets?”
// 3. “Are these numbers connected to previously known fraud networks?”

// 1. 
// To correlate Wangiri callers with their devices and geographies, you’d need to join three different tables.
// -- Find international callers using the same device or region
SELECT 
    c1.caller AS CallerA,
    c2.caller AS CallerB,
    d1.device_imei,
    r1.region_code
FROM cdrs c1
JOIN devices d1 ON c1.device_id = d1.device_id
JOIN regions r1 ON c1.region_id = r1.region_id
JOIN cdrs c2 
  ON c1.device_id = c2.device_id 
  OR c1.region_id = c2.region_id
WHERE c1.caller_country = 'INTL'
  AND c2.caller_country = 'INTL'
  AND c1.caller <> c2.caller
GROUP BY c1.caller, c2.caller, d1.device_imei, r1.region_code
HAVING COUNT(*) > 3
ORDER BY COUNT(*) DESC;


// In Neo4j, those links are natural traversals:
// Find callers connected by shared device or region
MATCH (a:PhoneNumber)-[:USES]->(d:Device)<-[:USES]-(b:PhoneNumber)
WHERE a <> b AND a.caller_country = "INTL" AND b.caller_country = "INTL"
RETURN a.number AS CallerA, b.number AS CallerB, d.imei AS sharedDevice
LIMIT 10;

UNION

MATCH (a:PhoneNumber)-[:LOCATED_IN]->(r:Region)<-[:LOCATED_IN]-(b:PhoneNumber)
WHERE a <> b
RETURN a.number AS CallerA, b.number AS CallerB, r.name AS sharedRegion
LIMIT 10;
