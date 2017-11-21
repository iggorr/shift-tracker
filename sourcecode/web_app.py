from flask import Flask, render_template, request, g
from datetime import date, timedelta
from calendar import monthrange
import sqlite3

app = Flask(__name__)
# Setting the path to the database
db_location = 'var/calendar.db'

# Function to get the current database connection
def get_db():
  db = getattr(g, 'db', None)
  if db is None:
    db = sqlite3.connect(db_location)
    g.db = db
    # Return database results as Row objects for easier operation
    db.row_factory = sqlite3.Row
  return db

# Function to query the database in a simpler way
def query_db(query, args=(), one=False):
  cur = get_db().execute(query, args)
  rv = cur.fetchall()
  cur.close()
  return (rv[0] if rf else None) if one else rv

# Function to insert values into a database  
def insert(table, values=()):
  cur = get_db().cursor()
  query = 'INSERT INTO %s VALUES (%s)' % (
    table,
    ', '.join(['?'] * len(values))
  )
  cur.execute(query, values)
  g.db.commit()
  id = cur.lastrowid
  cur.close()
  return id

# Function to close the database connection when the context is destroyed
@app.teardown_appcontext
def close_db_connection(exception):
  db = getattr(g, 'db', None)
  if db is not None:
    db.close()

# Function to initialise the database
def init_db():
  with app.app_context():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()

# Main route of the application that is used to display current and other
# month's views
@app.route('/')
@app.route('/<int:year>/<int:month>', methods=['GET', 'POST'])
def root(year=None, month=None):

  # Setting today's date as the current date
  current = date.today()
  # If year and month variables have been specified, 
  # set the passed year and month as the current ones
  if year and month:
    current = current.replace(year=year, month=month)

  # Calculating the last day in the current month
  last_day = monthrange(current.year, current.month)[1]
  # Finding the next month by adding a day to the last day of the month
  following_month = current.replace(day=last_day) + timedelta(days=1)
  # Calculating the weekday of the first day
  first_weekday = monthrange(current.year, current.month)[0]
  # Calculating the previous month by substracting 1 day from the first day of
  # the current month
  previous_month = current.replace(day=1) - timedelta(days=1)

  # Updating the calendar if the user POST'ed a request
  if request.method == 'POST':
    insert("events", [request.form['day'], current.month, current.year,
    request.form['description']])

  # Finding days of this month that contain an event and add them to a List
  populated = []
  sql = "SELECT * FROM events WHERE year=? AND month=?"
  for row in query_db(sql, [current.year, current.month]):
    populated.append(row['day'])

  # Passing the arguments into the template
  return render_template('calendar.html', current=current, last=last_day,
  following=following_month, first=first_weekday, previous=previous_month,
  populated=populated)

# Route for displaying the details of a day
@app.route('/<int:year>/<int:month>/<int:day>')
def day(year, month, day):
  return render_template('day.html', year=year, month=month, day=day)

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)

