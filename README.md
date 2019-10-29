# StockSim
cs411 project

TODO list:
1) Add front-end functionality where user types in a stock name they want info on.
      - In backend, write a view that uses this input to query db and return the stock info.
      - So we need to figure out how to use the data the form grabs as part of a function (a view maybe?)
           that will then query the database and return that information to the webpage. Our login page also
           does this whole process.

2) Add front-end functionality where user selects a buy or sell order and specifies his desired price

3) SOLVED Figure out how to get user input (buy/sell orders for example) so that it can be posted to db when
      needed.
      - Our login page gets and stores user info, so this would be a good starting point
 
4) Figure out how to periodically update database stock information
      - https://stackoverflow.com/questions/38285797/update-database-fields-hourly-with-python-django

Notes:
How to put data into webpage html template:
    - https://stackoverflow.com/questions/36950416/when-to-use-get-get-queryset-get-context-data-in-django
    - https://stackoverflow.com/questions/51631651/why-use-get-context-data-self-kwargs-and-super

About using SQL in Django:
Django has a very easy way to query/alter db with what are called "models." It would be nice to use this method of interacting with the db, but we have to make raw SQL statements for this project. See https://docs.djangoproject.com/en/2.2/topics/db/sql/
