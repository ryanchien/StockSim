CREATE TABLE UserTable (
    ID          INT,
    Username    VARCHAR(100) NOT NULL,
    Password    CHAR(100),
    Signup      DATE,
    PRIMARY KEY (username)
);

CREATE TABLE Game (
    GameID      INT NOT NULL,
    StartTime   DATE,
    EndTime     DATE,
    PRIMARY KEY GameID
);

CREATE TABLE Leaderboard (
    Username    VARCHAR(100) NOT NULL,
    Score       INT,
    FOREIGN KEY (Username) REFERENCES UserTable(Username)
);

CREATE TABLE Wallet (
    GameID      INT NOT NULL,
    TotalMoney  FLOAT,
    FOREIGN KEY (GameID) REFERENCES GameID
);

CREATE TABLE Stock (
    TickerSymbol    VARCHAR(4),
    Volume          FLOAT,
    Value           FLOAT,
    Company         VARCHAR(32),
    PRIMARY KEY TickerSymbol   
);

CREATE TABLE TradingHistory (
    TransactionID   INT IDENTITY(1,1) NOT NULL,   --replace AUTO_INCREMENT
    TimeOpened      DATE,
    TimeFilled      DATE,
    Price           FLOAT,
    Quantity        INT,
    PRIMARY KEY TransactionID
);


-- GET WALLET FOR A PARTICULAR USER

SELECT * FROM portfolio WHERE user = my_user;


-- ADD NEW ROW WHEN BUY
INSERT INTO portfolio
VALUES (username, stock, quantity, usd)

UPDATE portfolio
SET USD = new_usd
WHERE username=the_user

-- UPDATE ROW WHEN ALREADY HAVE THIS STOCK
UPDATE portfolio
SET quantity = prevQuant + newQuant
WHERE username=the_user AND stock = boughtstock

-- AGGREGATE TO MAP TOTAL QUANTITY OF STOCKS PER USER
SELECT username, SUM(quantity) as totalQ
FROM portfolio
GROUP BY username













