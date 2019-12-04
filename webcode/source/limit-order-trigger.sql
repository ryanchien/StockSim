-- TODO: 
    -- 1) in the front-end, need a button to insert an open limit buy order to TradingHistory.
    -- This will involve: 
        -- checking if the available USD quantity the user has is sufficient for order quantity
        -- updating Portfolios with subtracted USD of buy order (could be turned into a trigger)
        -- finally, inserting open buy order to TradingHistory
    
        -- for open sell orders, similar process:
            -- checking if the available Stock quantity user has is sufficient for order quantity
            -- updating Portfolios with subtracted Stock of sell order (could be turned into a trigger)
            -- finally, inserting open sell order to TradingHistory
    
    -- 2) in front-end, also need a button to delete an open limit buy order from TradingHistory.
        -- This will involve:
            -- checking if the record exists first. HOW WILL WE QUERY FOR THIS RECORD? Can we get the record ID
                -- from the front-end? (User, Symbol) wouldn't work as a key because user can have multiple orders on
                -- same symbol
            -- proceeding with delete statement on this record if so

        -- for open sell orders, exact same process.

    -- 3) Could add condition where old.OpenOrder = new.OpenOrder to avoid duplicating updates if this becomes a problem

-- Closes newly filled orders to activate other triggers that update db with this new info
CREATE TRIGGER CloseLimitOrder
    AFTER UPDATE OF Value ON Stocks
    FOR EACH ROW
    BEGIN
        UPDATE TradingHistory
        SET OpenOrder = 0
        WHERE OpenOrder = 1 AND
              old.TickerSymbol = Symbol AND
              ((BuySell = 'B' AND new.Value <= AskingPrice) OR (BuySell = 'S' AND new.Value >= AskingPrice));
    END;

-- Cascaded from CloseLimitOrder trigger, apply filled buy order to portfolio 
--      quantity previously 0, so must create new record
CREATE TRIGGER ApplyClosedBuyOrdersToNewRow
    AFTER UPDATE OF OpenOrder ON TradingHistory
    WHEN (old.BuySell = 'B' AND NOT EXISTS (SELECT * FROM Portfolios WHERE Symbol = old.Symbol AND Username = old.User))
    BEGIN
        INSERT INTO Portfolios
            VALUES (old.User, old.Symbol, old.Quantity);
    END;

CREATE TRIGGER ApplyClosedSellOrdersToNewRow
    AFTER UPDATE OF OpenOrder ON TradingHistory
    WHEN (old.BuySell = 'S' AND NOT EXISTS (SELECT * FROM Portfolios WHERE Symbol = 'USD' AND Username = old.User))
    BEGIN
        INSERT INTO Portfolios
            VALUES (old.User, 'USD', (old.Quantity * old.AskingPrice));
    END;

-- Cascaded from CloseLimitOrder trigger, apply filled buy order to portfolio
--      record exists, so add order quantity to current quantity
CREATE TRIGGER ApplyClosedBuyOrdersToExistingRow
    AFTER UPDATE OF OpenOrder ON TradingHistory
    FOR EACH ROW
    WHEN (old.BuySell = 'B' AND EXISTS (SELECT * FROM Portfolios WHERE Symbol = old.Symbol AND Username = old.User))
    BEGIN
        UPDATE Portfolios
            SET Quantity = Quantity + old.Quantity
            WHERE Symbol = old.Symbol AND
                  Username = old.User;
    END;

CREATE TRIGGER ApplyClosedSellOrdersToExistingRow
    AFTER UPDATE OF OpenOrder ON TradingHistory
    FOR EACH ROW
    WHEN (old.BuySell = 'S' AND EXISTS (SELECT * FROM Portfolios WHERE Symbol = 'USD' AND Username = old.User))
    BEGIN
        UPDATE Portfolios
            SET Quantity = Quantity + old.Quantity
            WHERE Symbol = 'USD' AND
                  Username = old.User;
    END;

-- When limit buy order is cancelled, want to reimburse escrow USD of user
CREATE TRIGGER ApplyCancelledBuyOrdersToExistingRow
    AFTER DELETE ON TradingHistory
    FOR EACH ROW
    WHEN (old.BuySell = 'B' AND EXISTS (SELECT * FROM Portfolios WHERE Symbol = 'USD' AND Username = old.User))
    BEGIN
        UPDATE Portfolios
            SET Quantity = Quantity + (old.Quantity * old.AskingPrice)
            WHERE Username = old.User AND
                  Symbol = 'USD';
    END;

CREATE TRIGGER ApplyCancelledSellOrdersToExistingRow
    AFTER DELETE ON TradingHistory
    FOR EACH ROW
    WHEN (old.BuySell = 'S' AND EXISTS (SELECT * FROM Portfolios WHERE Symbol = old.Symbol AND Username = old.User))
    BEGIN
        UPDATE Portfolios
            SET Quantity = Quantity + old.Quantity
            WHERE Username = old.User AND
                  Symbol = old.Symbol;
    END;

-- When limit buy order is cancelled, want to reimburse escrow USD of user
CREATE TRIGGER ApplyCancelledBuyOrdersToNewRow
    AFTER DELETE ON TradingHistory
    WHEN (old.BuySell = 'B' AND NOT EXISTS (SELECT * FROM Portfolios WHERE Symbol = 'USD' AND Username = old.User))
    BEGIN
        INSERT INTO Portfolios
            VALUES (old.User, 'USD', (old.Quantity * old.AskingPrice));
    END;

CREATE TRIGGER ApplyCancelledSellOrdersToNewRow
    AFTER DELETE ON TradingHistory
    WHEN (old.BuySell = 'S' AND NOT EXISTS (SELECT * FROM Portfolios WHERE Symbol = old.Symbol AND Username = old.User))
    BEGIN
        INSERT INTO Portfolios
            VALUES (old.User, old.Symbol, old.Quantity);
    END;

-- Would we need to have a separate trigger for when we make an order resulting in 0 USD in portfolio?
-- Since the logically invalid buy order (order where user has insufficient funds) will be handled in backend, 
    -- only need to consider equal to as an extra case
CREATE TRIGGER SubtractBuyOrderCostToEmpty
    BEFORE INSERT ON TradingHistory
    WHEN new.BuySell = 'B' AND 
         new.OpenOrder = 1 AND 
         (new.AskingPrice * new.Quantity) = (SELECT Quantity FROM Portfolios WHERE Username = new.User AND Symbol = 'USD')
    BEGIN
        DELETE FROM Portfolios
            WHERE Username = new.User AND Symbol = 'USD';
    END;

CREATE TRIGGER SubtractSellOrderCostToEmpty
    BEFORE INSERT ON TradingHistory
    WHEN new.BuySell = 'S' AND 
         new.OpenOrder = 1 AND 
         new.Quantity = (SELECT Quantity FROM Portfolios WHERE Username = new.User AND Symbol = new.Symbol)
    BEGIN
        DELETE FROM Portfolios
            WHERE Username = new.User AND Symbol = new.Symbol;
    END;

CREATE TRIGGER SubtractBuyOrderCost
    BEFORE INSERT ON TradingHistory
    WHEN new.BuySell = 'B' AND 
         new.OpenOrder = 1 AND 
         (new.AskingPrice * new.Quantity) <> (SELECT Quantity FROM Portfolios WHERE Username = new.User AND Symbol = 'USD')
    BEGIN
        UPDATE Portfolios
            SET Quantity = Quantity - (new.AskingPrice * new.Quantity)
            WHERE Username = new.User AND 
                  Symbol = 'USD';
    END;

CREATE TRIGGER SubtractSellOrderCost
    BEFORE INSERT ON TradingHistory
    WHEN new.BuySell = 'S' AND 
         new.OpenOrder = 1 AND 
         new.Quantity <> (SELECT Quantity FROM Portfolios WHERE Username = new.User AND Symbol = new.Symbol)
    BEGIN
        UPDATE Portfolios
            SET Quantity = Quantity - new.Quantity
            WHERE Username = new.User AND 
                  Symbol = new.Symbol;
    END;

CREATE TABLE TradingHistory (
    TimePurchased DATE NOT NULL,
    User TEXT NOT NULL,
    Symbol TEXT NOT NULL,
    AskingPrice FLOAT NOT NULL,
    Quantity INTEGER NOT NULL,
    BuySell Char(1),
    OpenOrder INT(1)
);     

    