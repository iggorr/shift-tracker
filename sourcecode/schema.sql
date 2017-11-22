DROP TABLE if EXISTS users;
DROP TABLE if EXISTS events;

CREATE TABLE users (
  username TEXT PRIMARY KEY,
  password TEXT,
  pay REAL
) WITHOUT ROWID;

CREATE TABLE events (
  day INTEGER,
  month INTEGER,
  year INTEGER,
  start_time TEXT,
  end_time TEXT,
  description TEXT,
  user TEXT,
  PRIMARY KEY (day, month, year)
);

INSERT INTO users VALUES ("igor", "12345", 8.07);
INSERT INTO events VALUES (19, 11, 2017, "05:30", "14:30", "Early Shift", "igor");
INSERT INTO events VALUES (22, 11, 2017, "14:30", "23:30", "Late Shift", "igor");

INSERT INTO users VALUES ("simon", "23456", 15.00);
INSERT INTO events VALUES (5, 11, 2017, "10:00", "18:00", "Mid Shift", "simon");
