// Constraints for uniqueness and performance
CREATE CONSTRAINT phone_number_unique IF NOT EXISTS
FOR (n:PhoneNumber) REQUIRE n.number IS UNIQUE;

CREATE CONSTRAINT subscriber_unique IF NOT EXISTS
FOR (s:Subscriber) REQUIRE s.subscriber_id IS UNIQUE;

CREATE CONSTRAINT device_unique IF NOT EXISTS
FOR (d:Device) REQUIRE d.imei IS UNIQUE;
