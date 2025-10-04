// Load phone numbers and link to subscribers
LOAD CSV WITH HEADERS FROM 'file:///numbers.csv' AS row
MERGE (n:PhoneNumber {number: row.number})
SET n.type = row.type, n.country = row.country
WITH n, row
MATCH (s:Subscriber {subscriber_id: toInteger(row.subscriber_id)})
MERGE (s)-[:OWNS]->(n);
