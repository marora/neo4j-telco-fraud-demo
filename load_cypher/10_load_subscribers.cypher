// Load subscribers from CSV
LOAD CSV WITH HEADERS FROM 'file:///subscribers.csv' AS row
MERGE (s:Subscriber {subscriber_id: toInteger(row.subscriber_id)})
SET s.name = row.name;
