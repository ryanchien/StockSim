from django.views.generic import TemplateView
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View, FormView
from django.conf import settings
import requests
from django.urls import reverse
import common.db_helper
from common.neo4j import User_Node, Transaction_Node, Portfolio_Node, Stock_Node

import time
import re
from datetime import date, timedelta

from django.views.generic import View, FormView
from .forms import StocksForm, BuySellForm, LimitForm
from django.shortcuts import get_object_or_404, redirect
#last_symbol = ""

from neomodel import config, db

config.DATABASE_URL = 'bolt://test:test@localhost:7687'  # default

class IndexPageView(TemplateView, FormView):
	
	template_name = 'main/index.html'


	#@staticmethod
	
	def get_form_class(self):
		url = self.request.get_full_path()
		if url == '/':
			return StocksForm

		if('Limit+Order' in self.request.get_full_path()):
			return LimitForm

		elif('stockdata=' in self.request.get_full_path() or '?tvwidgetsymbol=' in self.request.get_full_path()):
			return BuySellForm
		

		else:	
			return BuySellForm


	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		url = self.request.get_full_path()
		
		if('Limit+Order' in url):
			context['ord_type'] = 'Limit'
		else:
			context['ord_type'] = 'Market'
		# user = user.request.username
		# For now enter the username manually. This will be different for everyone
		user = self.request.user.username
		#print(user)
		sql_stocks = 'SELECT Symbol FROM Portfolios WHERE Symbol <> "USD" AND Username =? '
		args_stocks = (user,)
		recordstocks = common.db_helper.db_query(sql_stocks, args_stocks)
		sql_user_wallet = 'SELECT Quantity FROM Portfolios WHERE Username=? AND Symbol=?'
		args_user_wallet = (user, 'USD')
		record2 = common.db_helper.db_query(sql_user_wallet, args_user_wallet)
		user_wallet = 0
		if record2:
			user_wallet = record2[0]['Quantity']
		context['user_capital'] = user_wallet

		#print(type(recordstocks))
		#print("userstocks:")
		txt = ""
		userstocks = []
		for elem in recordstocks:
			userstocks.append(elem['Symbol'])

		if self.request.get_full_path() == '/':
			context['symbol'] = ''
			context['stocks'] = userstocks
			#QUERY HERE
#         if '?tvwidgetsymbol=' in self.request.get_full_path():
#                 print("got heregf adsgzdbghs")
#                 temp = (url.split('?tvwidgetsymbol=')[1])
#                 temp = temp.split('NASDAQ:')[1]
#                 print("thestock", temp)
#                 context['symbol'] = temp
		elif '?tvwidgetsymbol=' in self.request.get_full_path() and '?buysellvolume=' not in self.request.get_full_path():
			temp = (url.split('?tvwidgetsymbol=')[1])
			context['symbol'] = temp


		elif 'stockdata=' in self.request.get_full_path() and '?buysellvolume=' not in self.request.get_full_path():
			temp = (url.split('stockdata=')[1])
			context['symbol'] = temp


			#last_symbol = url.split('?stockdata=')[1]
		elif 'cancelOrder' in self.request.get_full_path():
			order_id =  (re.search('cancelOrder(.*)=cancel', self.request.get_full_path()).group(1))
			sql_cancel = 'DELETE FROM TradingHistory WHERE rowid=?'
			args_cancel = (order_id,)
			common.db_helper.db_execute(sql_cancel, args_cancel)

		elif 'stockdata=' in self.request.get_full_path() and '?buysellvolume=' in self.request.get_full_path():
			temp = url.split('?buysellvolume=')
			quantity = int((temp[1])[: temp[1].find('&')])
			temp = (url.split('stockdata='))[1]
			symbol = temp[ : temp.find('&')]
			#print(symbol)
			
			# get price of stock
			sql1 = 'SELECT Value FROM Stocks WHERE TickerSymbol=?'
			args1 = (symbol,)
			record1 = common.db_helper.db_query(sql1, args1)
			price = record1[0]['Value']

			# get user's current USD
			sql2 = 'SELECT Quantity FROM Portfolios WHERE Username=? AND Symbol=?'
			args2 = (user, 'USD')
			record2 = common.db_helper.db_query(sql2, args2)
			current_USD_in_wallet = 0
			if record2:
				current_USD_in_wallet = record2[0]['Quantity']
			# get user's current stock quantity
			sql3 = 'SELECT Quantity FROM Portfolios WHERE Username=? AND Symbol=?'
			args3 = (user, symbol)
			record3 = common.db_helper.db_query(sql3, args3)
			if record3:
				current_stock_in_wallet = record3[0]['Quantity']
			else:
				# This means no record of user + stock exists. Create new entry later if valid
				current_stock_in_wallet = 0

			order_cost = quantity * price

			# Begin applying order to user's portfolio...
			if re.search('buy=', self.request.get_full_path()):

				result = re.search('orderprice=(\\d+)', self.request.get_full_path())

				if result:
					# limit buy order

					# checking if the available USD quantity the user has is sufficient for order quantity
        			# updating Portfolios with subtracted USD of buy order (could be turned into a trigger)
        			# finally, inserting open buy order to TradingHistory
					# CREATE TABLE TradingHistory (
					#     TimePurchased DATE NOT NULL,
					#     User TEXT NOT NULL,
					#     Symbol TEXT NOT NULL,
					#     AskingPrice FLOAT NOT NULL,
					#     Quantity INTEGER NOT NULL,
					#     BuySell Char(1),
					#     OpenOrder INT(1)
					# );    

					orderprice = int(result[1])
					order_cost = quantity * orderprice

					if current_USD_in_wallet >= order_cost:
						#@TODO: Consider the case where the limit order gets filled automatically 
						#if orderprice <= price:

						sql_create_open_order = 'INSERT INTO TradingHistory VALUES (?,?,?,?,?,?,?)'
						args_create_open_order = (time.strftime('%Y-%m-%d %H:%M:%S'), user, symbol, orderprice, quantity, 'B', 1)
						common.db_helper.db_execute(sql_create_open_order, args_create_open_order)

				else:

					# market buy order
					if current_USD_in_wallet >= order_cost:
						if current_stock_in_wallet == 0:
							# Should be no record in database if quantity is 0, therefore create new user-stock record
							sql6 = 'INSERT INTO Portfolios VALUES (?,?,?)'
							args6 = (user, symbol, quantity)
							common.db_helper.db_execute(sql6, args6)

						# Update with increased stock quantity
						sql4 = 'UPDATE Portfolios SET Quantity=? WHERE Username=? AND Symbol=?'
						updated_stock_quantity = current_stock_in_wallet + quantity
						args4 = (updated_stock_quantity, user, symbol)
						common.db_helper.db_execute(sql4, args4)

						# Update with decreased USD quantity
						sql5 = 'UPDATE Portfolios SET Quantity=? WHERE Username=? AND Symbol=?'
						updated_USD_quantity = current_USD_in_wallet - order_cost
						args5 = (updated_USD_quantity, user, "USD")
						common.db_helper.db_execute(sql5, args5)
						context['user_capital'] = updated_USD_quantity

						# Update neo4j nodes
						neo4j_query0 = "MATCH (s:Stock_Node) WHERE s.symbol='{stocksymbol}' RETURN s;".format(stocksymbol=symbol)
						stock_node_list = db.cypher_query(neo4j_query0)
						if (len(stock_node_list[0])==0):
							stock_node_list = Stock_Node(symbol=symbol, curr_price=price).save()

						neo4j_query1 = "MATCH (a:User_Node)-[:OWNS]->(s:Stock_Node) WHERE a.uid='{username}' AND s.symbol='{stocksymbol}' WITH a, collect(DISTINCT s.symbol) as listStocks RETURN listStocks;".format(username=user, stocksymbol=symbol)
						owned_stock_list = db.cypher_query(neo4j_query1)
						#print(owned_stock_list)
						if (len(owned_stock_list[0])==0):
							user_node = User_Node.nodes.get(uid=user)
							stock_node = Stock_Node.nodes.get(symbol=symbol)
							user_node.stock.connect(stock_node)
							port_node = Portfolio_Node(uid=user, symbol=symbol, profit=0.0, quantity=quantity).save()
							user_node.portfolio.connect(port_node)
							port_node.stock.connect(stock_node)
						else:
							#print("already owns stock")
							port_node = Portfolio_Node.nodes.get(uid=user, symbol=symbol)
							port_node.quantity += quantity
							port_node.save()

						# Update transaction history
						sql7 = 'INSERT INTO TradingHistory (TimePurchased, AskingPrice, Quantity, User, Symbol, BuySell, OpenOrder) VALUES (?,?,?,?,?,?,?)'
						args7 = (time.strftime('%Y-%m-%d %H:%M:%S'),price,quantity,user,symbol,'B', 0)
						common.db_helper.db_execute(sql7, args7)
						
						trans_node = Transaction_Node(price=price, buy=True, quantity=quantity,date=date.today()).save()
						user_node = User_Node.nodes.get(uid=user)
						stock_node = Stock_Node.nodes.get(symbol=symbol)
						user_node.transaction.connect(trans_node)
						trans_node.stock.connect(stock_node)

						#print(time.strftime('%Y-%m-%d %H:%M:%S') + " " + str(price) + " " + str(quantity) + " "  + user)
			elif re.search('sell=', self.request.get_full_path()):

				result = re.search('orderprice=(\\d+)', self.request.get_full_path())

				if result: 
					orderprice = int(result[1])
					order_cost = quantity * orderprice

					if current_stock_in_wallet >= quantity:
						# NOTE: We aren't going to handle the case where user enters more quantity than he has to sell.
						#		We will just ignore this case and not open a partial order as we did for market orders.

						#@TODO: Consider the case where the limit order gets filled automatically. Currently would have to wait
						#		for next price update.
						#		if orderprice <= price:

						sql_create_open_order = 'INSERT INTO TradingHistory VALUES (?,?,?,?,?,?,?)'
						args_create_open_order = (time.strftime('%Y-%m-%d %H:%M:%S'), user, symbol, orderprice, quantity, 'S', 1)
						common.db_helper.db_execute(sql_create_open_order, args_create_open_order)
				else:		
					# is market sell order
					quantity *= -1

					if current_stock_in_wallet <= abs(quantity):
						# If user asks to sell more than he has, sell only his remaining stock.
						# Since quantity will reach 0, delete existing user-stock record
						updated_stock_quantity = 0
						updated_USD_quantity = current_USD_in_wallet + (current_stock_in_wallet * price)

						# Delete user-stock record from database
						sql7 = 'DELETE FROM Portfolios WHERE Username=? AND Symbol=?'
						args7 = (user, symbol)
						common.db_helper.db_execute(sql7, args7)

						port_node = Portfolio_Node.nodes.get(uid=user, symbol=symbol)
						user_node = User_Node.nodes.get(uid=user)
						stock_node = Stock_Node.nodes.get(symbol=symbol)
						port_node.delete()
						user_node.stock.disconnect(stock_node)


					else:
						updated_USD_quantity = current_USD_in_wallet + order_cost
						port_node = Portfolio_Node.nodes.get(uid=user, symbol=symbol)
						port_node.quantity -= abs(quantity)
						port_node.save()

					context['user_capital'] = updated_USD_quantity

					sql8 = 'INSERT INTO TradingHistory (TimePurchased, AskingPrice, Quantity, User, Symbol, BuySell, OpenOrder) VALUES (?,?,?,?,?,?,?)'
					args8 = (time.strftime('%Y-%m-%d %H:%M:%S'),price,abs(quantity),user,symbol,'S', 0)
					common.db_helper.db_execute(sql8, args8)

					trans_node = Transaction_Node(price=price, buy=False, quantity=abs(quantity), date=date.today()).save()
					user_node = User_Node.nodes.get(uid=user)
					stock_node = Stock_Node.nodes.get(symbol=symbol)
					user_node.transaction.connect(trans_node)
					trans_node.stock.connect(stock_node)



					# Since quantity is currently just negative for sell orders, we will add quantity

					# Update with decreased stock quantity
					sql4 = 'UPDATE Portfolios SET Quantity=? WHERE Username=? AND Symbol=?'
					updated_stock_quantity = current_stock_in_wallet + quantity
					args4 = (updated_stock_quantity, user, symbol)
					common.db_helper.db_execute(sql4, args4)
					

					# Update with increased USD quantity
					sql5 = 'UPDATE Portfolios SET Quantity=? WHERE Username=? AND Symbol=?'
					args5 = (updated_USD_quantity, user, "USD")
					common.db_helper.db_execute(sql5, args5)

			#update neo4j portfolio profit
			sell = 0.0
			potential = 0.0
			buy = 0.0
			transaction_node_exists = True
			neo4j_buy_query = "MATCH (a:User_Node)-[:PERFORMS]->(t:Transaction_Node)-[:TRANSACTIONTOSTOCK]->(s:Stock_Node) WHERE a.uid = '{username}' AND s.symbol = '{stocksymbol}' AND t.buy = true RETURN SUM(t.price * t.quantity);".format(username=user, stocksymbol=symbol)
			buy = db.cypher_query(neo4j_buy_query)
			if (len(buy[0])==0):
				transaction_node_exists = False
			if (transaction_node_exists == True):
				buy = buy[0][0][0]
			neo4j_sell_query = "MATCH (a:User_Node)-[:PERFORMS]->(t:Transaction_Node)-[:TRANSACTIONTOSTOCK]->(s:Stock_Node) WHERE a.uid = '{username}' AND s.symbol = '{stocksymbol}' AND t.buy = false RETURN SUM(t.price * t.quantity);".format(username=user, stocksymbol=symbol)
			sell = db.cypher_query(neo4j_sell_query)
			if (len(sell[0])==0):
				transaction_node_exists = False
			if (transaction_node_exists == True):
				sell = sell[0][0][0]
			neo4j_potential_query = "MATCH (s:Stock_Node)<-[:OWNS]-(a:User_Node)-[:HASPORTFOLIO]->(p:Portfolio_Node) WHERE s.symbol = '{stocksymbol}' AND a.uid = '{username}' AND p.symbol = '{stocksymbol}' RETURN s.curr_price * p.quantity AS potential;".format(username=user, stocksymbol=symbol)
			potential = db.cypher_query(neo4j_potential_query)
			if (len(potential[0])==0):
				transaction_node_exists = False
			if (transaction_node_exists == True):
				potential = potential[0][0][0]


			if (transaction_node_exists == True):
				port_node = Portfolio_Node.nodes.get(uid=user, symbol=symbol)
				port_node.profit = (sell + potential)/buy
				port_node.save()

			neo4j_better_profit_query = "MATCH (p:Portfolio_Node)-[:CONTAINS]->(s:Stock_Node)<-[:CONTAINS]-(p1:Portfolio_Node) WHERE p.uid='{username}' AND p1.profit > p.profit AND s.symbol = '{stocksymbol}' RETURN p1.uid ORDER BY p1.profit DESC;".format(username=user, stocksymbol=symbol)
			better_users = db.cypher_query(neo4j_better_profit_query)
			#print(better_users)
			better_list = better_users[0]
			tup_list = []
			idx = 1
			for better in better_list:
				uid = better[0]
				neo4j_selldate_query = "MATCH (s:Stock_Node)<-[:TRANSACTIONTOSTOCK]-(ts:Transaction_Node)<-[:PERFORMS]-(betterTrader:User_Node) WHERE ts.buy = false AND s.symbol = '{stocksymbol}' AND betterTrader.uid='{username}' WITH max(ts.price) as maxsell MATCH (s:Stock_Node)<-[:TRANSACTIONTOSTOCK]-(ts:Transaction_Node)<-[:PERFORMS]-(betterTrader:User_Node) WHERE ts.price = maxsell AND ts.buy = false AND s.symbol = '{stocksymbol}' AND betterTrader.uid='{username}' RETURN ts.date, ts.tid".format(stocksymbol=symbol, username=uid)
				selldate = db.cypher_query(neo4j_selldate_query)
				neo4j_buydate_query = "MATCH (s:Stock_Node)<-[:TRANSACTIONTOSTOCK]-(ts:Transaction_Node)<-[:PERFORMS]-(betterTrader:User_Node) WHERE ts.buy = true AND s.symbol = '{stocksymbol}' AND betterTrader.uid='{username}' WITH min(ts.price) as minbuy MATCH (s:Stock_Node)<-[:TRANSACTIONTOSTOCK]-(ts:Transaction_Node)<-[:PERFORMS]-(betterTrader:User_Node) WHERE ts.price = minbuy AND ts.buy = true AND s.symbol = '{stocksymbol}' AND betterTrader.uid='{username}' RETURN ts.date, ts.tid".format(stocksymbol=symbol, username=uid)
				buydate = db.cypher_query(neo4j_buydate_query)
				tup = (idx, uid, selldate[0][0][0], buydate[0][0][0])
				idx+=1
				tup_list.append(tup)
				print("the list", tup_list)
				context['better_orders'] = tup_list
			url = self.request.get_full_path()
			temp = url.split('?buysellvolume=')
			context['volume'] = (temp[1])[: temp[1].find('&')]
			temp = (url.split('stockdata='))[1]
			context['symbol'] = temp[ : temp.find('&')]
		stock_quant_sql = 'SELECT Symbol, Quantity FROM Portfolios WHERE Symbol <> "USD" AND Username =? '
		argsstocks = (user,)
		stock_quantities_query = common.db_helper.db_query(stock_quant_sql, argsstocks)
		stock_quantities = [(d['Symbol'], int(d['Quantity'])) for d in stock_quantities_query]
		context['stock_quantity'] = stock_quantities
		sql_open_orders = 'SELECT rowid, Symbol,AskingPrice, Quantity, BuySell FROM TradingHistory WHERE User =? AND OpenOrder = 1'
		args_open_orders = (user,)
		open_orders_query = common.db_helper.db_query(sql_open_orders, args_open_orders)
		open_orders = [(row['rowid'], row['Symbol'],row['AskingPrice'] ,int(row['Quantity']), row['BuySell']) for row in open_orders_query]
		print("OPEN ORDERS", open_orders)
		context['open_orders'] = open_orders
		context['user_capital'] = user_wallet

		return context


    #return render(request, 'new/click.html',{'value':'Button clicked'})
	




class ChangeLanguageView(TemplateView):
    template_name = 'main/change_language.html'