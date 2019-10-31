
For the rest of the project, we aim to use every stock from our World Trading Data API and not limit to NASDAQ (we might have to use MongoDB instead of SQL in order to scale the app for this kind of data, do we?)
The global idea is to have a nice user interface where you can easily look at stock prices, click on one, the app should give you advice on your potential purchase based on profit made by other users for this stock.
Then you can buy it or sell it if it’s already in your wallet. Once you have it, you should be able to assess how your trading strategy is going on using data from other users of the simulator.

We also want to set up some kind of ranking among users, the comparison criteria is not yet defined, but we thought about net profit,    P/E ratio (Derek you cited some of them)


2 advanced functions (usefulness, technical difficulties, novelty)

AF 1 - SQL
- Using a SQL Procedure that would execute each time a user wants to buy a specific stock A, we can assess the stock’s performance using a grade scale.
In order to do this we need in our portfolio to store the purchase price of each stock which would change our database structure as we currently only update quantity when an existing stock is bought. Then by comparing the price between purchase and current price from API, we could compute the mean or median for all users having stock A and give it a grade according to the profit they made.

It is useful for the users because it allows them to better assess the choice they are making buying a specific stock and avoid them some mistake if everyone has been loosing money on it.
The technical difficulty would be the computation time / efficiency because with a lot of users and as it needs the real time price we need to compute this each time a user is interested by a stock, it can be computationally expensive.
Also as we have to change the structure of our database and find a new well suited one that could store the purchase price for every stock and every user.


AF 2 - NoSQL:

- Using Neo4j and a graph structure with every user and stocks, we can have relation between user and stock for who owns which stock and from this we could evaluate where the user is doing better.
Also, we could find interesting relations between users. For a user A, we could find all other users that have bought the same stock, limit to those that made more profit on it and compare the strategy (date of purchase).


The novelty in this function is the user relation idea that is very rare in trading platforms where you basically have a ranking to compare but don’t really learn from others. This is also why it is useful, you can learn in real time why you did not make more money by knowing if you were to early or too late in your purchase. It allows to gain experience and make better next time. 