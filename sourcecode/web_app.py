from flask import Flask, render_template, request, g, redirect, url_for
from datetime import date, datetime, timedelta
from calendar import monthrange
import sqlite3

app = Flask(__name__)
# Setting the path to the database
db_location = 'var/calendar.db'
# Setting the user
user = None

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
  return (rv[0] if rv else None) if one else rv

# Function to insert values into a database  
def insert(table, values=()):
  cur = get_db().cursor()
  query = 'INSERT OR REPLACE INTO %s VALUES (%s)' % (
    table,
    ', '.join(['?'] * len(values))
  )
  cur.execute(query, values)
  get_db().commit()
  cur.close()

# Function to delete a row from the database
def delete(table, values=()):
  cur = get_db().cursor()
  query = 'DELETE FROM %s WHERE day=? AND month=? AND year=? AND user=?' % (table)
  cur.execute(query, values)
  get_db().commit()
  cur.close

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

# Error handler for 404
@app.errorhandler(404)
def page_not_found(error):
  # Redirect to the root route
  return redirect(url_for('root'))

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
  # Display if currently not logged in
  global user
  if not user:
    # If simply accessing the page
    if request.method == 'GET':
      return render_template('login.html') 
    # If attempting to login, query credentials against database
    else:
      sql = "SELECT * FROM users WHERE username=? AND password=?"
      # If not successful - try again
      if not query_db(sql, [request.form['username'], request.form['password']], one=True):
        return render_template('login.html')
      else:
        user = request.form['username']
  # If logged in proceed to root page
  return redirect(url_for('root'))

# Function to logout
@app.route('/logout')
def logout():
  global user
  user = None
  return redirect(url_for('root'))

# Main route of the application that is used to display current and other
# month's views
@app.route('/')
@app.route('/<int:year>/<int:month>', methods=['GET', 'POST'])
def root(year=None, month=None):

  # Checking if user's logged in, if not redirect to login page
  if not user:
    return redirect(url_for('login'))
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

  # Making changes to the calendar if the user POST'ed a request
  if request.method == 'POST':
    # Add new event if the user created one
    if request.form['action'] == 'Save':
      insert("events", [request.form['day'], current.month, current.year,
      request.form['start_time'], request.form['end_time'],
      request.form['description'], user])
    # Otherwise delete the event
    else:
      delete("events", [request.form['day'], current.month, current.year, user])

  # Finding days of this month that contain a shift and add them to a dictionary
  populated = {}
  shifts = 0
  total_hours = 0
  earned = 0

  # Query user details
  sql = "SELECT * FROM users WHERE username=?"
  user_details = query_db(sql, [user], one=True)

  sql = "SELECT day, start_time, end_time FROM events WHERE year=? AND month=? AND user=?"
  for row in query_db(sql, [current.year, current.month, user]):
    shifts += 1
    time_format = '%H:%M'
    duration = datetime.strptime(row['end_time'], time_format) - datetime.strptime(row['start_time'], time_format)
    duration_rounded = duration.total_seconds() / 3600.0
    total_hours += duration_rounded
    earned += user_details['pay'] * duration_rounded
    populated[row['day']] = {'start_time': row['start_time'], 'end_time':
    row['end_time'], 'duration': duration_rounded}

  # Passing the arguments into the template
  return render_template('calendar.html', current=current, last=last_day,
  following=following_month, first=first_weekday, previous=previous_month,
  populated=populated, shifts=shifts, total=total_hours, user=user_details,
  earned=earned)

# Route for displaying the details of a day
@app.route('/<int:year>/<int:month>/<int:day>')
def day(year, month, day):

  # Checking if user's logged in, if not redirect to login page
  if not user:
    return redirect(url_for('login'))

  # Quering the database to see whether the day has an event
  sql = "SELECT * FROM events WHERE year=? AND month=? AND day=? AND user=?"
  event = query_db(sql, [year, month, day, user], one=True)
  time_format = '%H:%M'
  if event:
    duration = datetime.strptime(event['end_time'], time_format) - datetime.strptime(event['start_time'], time_format)
    duration_rounded = duration.total_seconds() / 3600.0
  else:
    duration_rounded = None
  return render_template('day.html', year=year, month=month, day=day,
  event=event, duration=duration_rounded)

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)

