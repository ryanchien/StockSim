# StockSim
cs411 project

TODO list:
1) Front-end: user types in a stock name they want info on and the info gets returned.
      - In backend, write a view that uses this input to query db and return the stock info.
      - So we need to figure out how to use the data the form grabs as part of a function (a view maybe?)
           that will then query the database and return that information to the webpage. Our login page also
           does this whole process.

2) Front-end: user selects a buy or sell order, specifies his desired price + quantity, it gets checked for sufficient funds, it gets logged in db (order + escrow (portfolio?)), the list of the user's active orders gets updated and displayed to the user.

3) Back-end: db triggers for updating order table and user portfolio table when prices change and meet order specifics.
 
4) Back-end: Figure out how to periodically update database stock information.
      - https://stackoverflow.com/questions/38285797/update-database-fields-hourly-with-python-django

5) Back-end (Peter): Figure out procedure for using user input to query/alter db and relay info back to user.
      - Current hunch is to combine a form with a view and redirect to the same page to refresh.
      
6) Front-end: user presses cancel button next to an active order, it gets logged in database appropriately.

7) Back-end: refering to #2, figure out what to do with escrow. We need a way to distinguish a user's available funds from his funds that are currently put into active buy/sell orders. That goes for stocks as well.
      
Notes:
How to put data into webpage html template:
    - https://stackoverflow.com/questions/36950416/when-to-use-get-get-queryset-get-context-data-in-django
    - https://stackoverflow.com/questions/51631651/why-use-get-context-data-self-kwargs-and-super

About using SQL in Django:
 - Django has a very easy way to query/alter db with what are called "models." It would be nice to use this method of interacting with the db, but we have to make raw SQL statements for this project. See https://docs.djangoproject.com/en/2.2/topics/db/sql/
 - We are currently using the sqlite3 library to interact with the sqlite db instead of django's built in db library. If we ever need to switch to a different database (sqlite3 is one of the more limited db systems), its easy to change django's provided db to another db system, so we might as well just start using django's built in db library at that point.
