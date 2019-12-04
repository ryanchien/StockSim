-- Closes newly filled orders to activate other triggers that update db with this new info
CREATE TRIGGER CloseLimitOrder
    AFTER UPDATE OF Value ON Stocks
    FOR EACH ROW
    BEGIN
        UPDATE TradingHistory
        SET OpenOrder = 0
        WHERE OpenOrder = 1 AND
              old.TickerSymbol = Symbol AND
              BuySell = 'B' AND
              new.Value <= AskingPrice;
    END;

-- Cascaded from CloseLimitOrder trigger
CREATE TRIGGER ApplyClosedBuyOrdersToNew
    AFTER UPDATE OF OpenOrder ON TradingHistory
    WHEN (old.BuySell = 'B' AND NOT EXISTS (SELECT * FROM Portfolios WHERE Symbol = old.Symbol AND Username = old.User))
    BEGIN
        INSERT INTO Portfolios
            VALUES (old.User, old.Symbol, old.Quantity);
    END;

-- Cascaded from CloseLimitOrder trigger        
CREATE TRIGGER ApplyClosedBuyOrdersToExisting
    AFTER UPDATE OF OpenOrder ON TradingHistory
    FOR EACH ROW
    WHEN (old.BuySell = 'B' AND EXISTS (SELECT * FROM Portfolios WHERE Symbol = old.Symbol AND Username = old.User))
    BEGIN
        UPDATE Portfolios
            SET Quantity = Quantity + old.Quantity
            WHERE old.Symbol = Symbol AND
                  old.User = Username;
    END;
        
CREATE TABLE TradingHistory (
User CHAR(256),
Symbol Char(256),
AskingPrice FLOAT,
Quantity INTEGER,
BuySell Char(1),
OpenOrder INT(1)
);     

    