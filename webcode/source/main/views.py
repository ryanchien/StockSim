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
import time

from django.views.generic import View, FormView
from .forms import StocksForm, BuySellForm
from django.shortcuts import get_object_or_404, redirect

#last_symbol = ""

class IndexPageView(TemplateView, FormView):
	template_name = 'main/index.html'


	#@staticmethod
	
	def get_form_class(self):
		url = self.request.get_full_path()
		if url == '/':
			return StocksForm
		else:	
			return BuySellForm


	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		url = self.request.get_full_path()
		# user = user.request.username
		# For now enter the username manually. This will be different for everyone
		user = self.request.user.username
		#print(user)
		sqlstocks = 'SELECT * FROM Portfolios WHERE Symbol <> "USD"; '
		argsstocks = (user,)
		recordstocks = common.db_helper.db_query(sqlstocks)
		#print(type(recordstocks))
		#print("userstocks:")
		txt = ""
		userstocks = []
		for elem in recordstocks:
			userstocks.append(elem['Symbol'])

		if self.request.get_full_path() == '/':
			context['symbol'] = ''
			context['stocks'] = userstocks#QUERY HERE
		elif '?stockdata=' in self.request.get_full_path() and '?buysellvolume=' not in self.request.get_full_path():
			temp = (url.split('?stockdata=')[1])
			context['symbol'] = temp
			#last_symbol = url.split('?stockdata=')[1]
		elif '&stockdata=' in self.request.get_full_path() and '?buysellvolume=' in self.request.get_full_path():
			temp = url.split('?buysellvolume=')
			quantity = int((temp[1])[: temp[1].find('&')])
			temp = (url.split('&stockdata='))[1]
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
			if self.request.get_full_path().split("&")[2] == 'buy=':
				# buy order
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

					# Update transaction history
					sql7 = 'INSERT INTO TradingHistory (TimePurchased, Price, Quantity, User, Symbol, BuySell) VALUES (?,?,?,?,?,?)'
					args7 = (time.strftime('%Y-%m-%d %H:%M:%S'),price,quantity,user,symbol,'B')
					common.db_helper.db_execute(sql7, args7)

					print(time.strftime('%Y-%m-%d %H:%M:%S') + " " + str(price) + " " + str(quantity) + " "  + user)
			elif self.request.get_full_path().split("&")[2] == 'sell=':
				quantity *= -1
				# sell order
				if current_stock_in_wallet <= abs(quantity):
					# If user asks to sell more than he has, sell only his remaining stock.
					# Since quantity will reach 0, delete existing user-stock record
					updated_stock_quantity = 0
					updated_USD_quantity = current_USD_in_wallet + (current_stock_in_wallet * price)

					# Delete user-stock record from database
					sql7 = 'DELETE FROM Portfolios WHERE Username=? AND Symbol=?'
					args7 = (user, symbol)
					common.db_helper.db_execute(sql7, args7)
				else:
					updated_USD_quantity = current_USD_in_wallet + order_cost

				sql8 = 'INSERT INTO TradingHistory (TimePurchased, Price, Quantity, User, Symbol, BuySell) VALUES (?,?,?,?,?,?)'
				args8 = (time.strftime('%Y-%m-%d %H:%M:%S'),price,abs(quantity),user,symbol,'S')
				common.db_helper.db_execute(sql8, args8)


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

			url = self.request.get_full_path()
			temp = url.split('?buysellvolume=')
			context['volume'] = (temp[1])[: temp[1].find('&')]
			temp = (url.split('&stockdata='))[1]
			#print(temp)
			context['symbol'] = temp[ : temp.find('&')]
		return context


'''
	def form_valid(self, form):
		print("okokokok")
		request = self.request
		if isinstance(form, StocksForm):
			print("symbol")
			return redirect('symbol', symbol=form.cleaned_data['stockdata'])
		elif isinstance(form, BuySellForm):
			print("volume")
			return redirect('volume', symbol=self.request.get_full_path(), volume=form.cleaned_data['buysellvolume'])
		print("doing")
		return redirect('index')
'''
	
'''
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		# This is just an example of how to query the db to pull information.
		# To use this we just need
		sql = 'SELECT * FROM Stock WHERE TickerSymbol=?'
		arg = ('APPL',)
		record = common.db_helper.db_query(sql, arg)
		if record:
			context['symbol'] = record['TickerSymbol']
		else:
			context['symbol'] = 'Does not exist'
		return context
'''




class ChangeLanguageView(TemplateView):
    template_name = 'main/change_language.html'