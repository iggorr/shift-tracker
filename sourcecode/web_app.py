from flask import Flask, render_template
from datetime import date, timedelta
from calendar import monthrange

app = Flask(__name__)

# Main route of the application that is used to display current and other
# month's views
@app.route('/')
@app.route('/<int:year>/<int:month>')
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
  # Passing the arguments into the template
  return render_template('main.html', current=current, last=last_day,
  following=following_month, first=first_weekday, previous=previous_month)

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)

