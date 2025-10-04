// 99_validate.cypher
// Validation checks after data load

// Count by label
MATCH (s:Subscriber) RETURN 'Subscribers' AS label, count(s) AS count
UNION ALL
MATCH (n:PhoneNumber) RETURN 'PhoneNumbers' AS label, count(n) AS count
UNION ALL
MATCH (d:Device) RETURN 'Devices' AS label, count(d) AS count;

// Count relationships
MATCH ()-[c:CALLS]->() RETURN 'CALLS' AS relType, count(c) AS count
UNION ALL
MATCH ()-[r:OWNS]->() RETURN 'OWNS' AS relType, count(r) AS count
UNION ALL
MATCH ()-[r:USES]->() RETURN 'USES' AS relType, count(r) AS count;

