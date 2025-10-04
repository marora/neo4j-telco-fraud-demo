// Load call detail records as CALLS relationships
LOAD CSV WITH HEADERS FROM 'file:///cdrs.csv' AS row
MERGE (caller:PhoneNumber {number: row.caller})
MERGE (callee:PhoneNumber {number: row.callee})
MERGE (caller)-[c:CALLS {ts: toInteger(row.timestamp), start: row.start_time}]->(callee)
SET c.duration = toInteger(row.duration),
    c.cost = toFloat(row.cost),
    c.caller_device = row.caller_device,
    c.callee_device = row.callee_device,
    c.caller_country = row.caller_country,
    c.callee_country = row.callee_country;
