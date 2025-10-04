// Load devices
LOAD CSV WITH HEADERS FROM 'file:///devices.csv' AS row
MERGE (d:Device {imei: row.imei})
SET d.device_id = row.device_id, d.ip = row.ip;
