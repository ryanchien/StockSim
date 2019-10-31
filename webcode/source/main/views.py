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

		
		if self.request.get_full_path() == '/':
			context['symbol'] = ''
		elif '?stockdata=' in self.request.get_full_path() and '?buysellvolume=' not in self.request.get_full_path():
			url = self.request.get_full_path()
			temp = (url.split('?stockdata=')[1])
			context['symbol'] = temp
			#last_symbol = url.split('?stockdata=')[1]
		elif '&stockdata=' in self.request.get_full_path() and '?buysellvolume=' in self.request.get_full_path():
			url = self.request.get_full_path()
			temp = url.split('?buysellvolume=')
			context['volume'] = (temp[1])[: temp[1].find('&')]
			temp = (url.split('&stockdata='))[1]
			print(temp)
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