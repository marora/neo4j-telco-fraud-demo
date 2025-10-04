// Fraud Ring detection using GDS Louvain community detection
CALL gds.graph.project(
  'fraudCalls',
  ['PhoneNumber'],
  {
    CALLS: {
      orientation: 'UNDIRECTED',
      properties: ['duration', 'cost']
    }
  }
);

CALL gds.louvain.stream('fraudCalls')
YIELD nodeId, communityId
WITH gds.util.asNode(nodeId) AS phone, communityId
RETURN communityId, collect(phone.number)[0..10] AS sampleNumbers, count(*) AS communitySize
ORDER BY communitySize DESC
LIMIT 10;
