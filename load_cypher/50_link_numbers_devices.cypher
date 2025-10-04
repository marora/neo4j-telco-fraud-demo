// Attach numbers to devices where possible (from caller_device field)
LOAD CSV WITH HEADERS FROM 'file:///cdrs.csv' AS row
WITH row 
WHERE row.caller_device IS NOT NULL 
  AND row.caller_device <> "" 
  AND row.caller_device <> "UNKNOWN" 
  AND row.caller_device <> "EXT"
MATCH (p:PhoneNumber {number: row.caller})
MERGE (d:Device {imei: row.caller_device})   // ensures SIMBOX_IMEI devices get created
MERGE (p)-[:USES]->(d);
