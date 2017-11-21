DROP TABLE if EXISTS events;

CREATE TABLE events (
  day integer,
  month integer,
  year integer,
  description text
);

INSERT INTO events VALUES (19, 11, 2017, "Early Shift");
INSERT INTO events VALUES (22, 11, 2017, "Bla Shift");
