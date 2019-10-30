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

class IndexPageView(TemplateView, FormView):
	template_name = 'main/index.html'


	#@staticmethod
	def get_form_class(self):
		if self.request.get_full_path() == '/':
			return StocksForm
		else:
			return BuySellForm

	def form_valid(self, form):
		request = self.request
		if isinstance(form, StocksForm):
			return redirect('index', symbol=form.cleaned_data['stockdata'])
		elif isinstance(form, BuySellForm):
			return redirect('index', symbol=self.request.get_full_path(), volume=form.cleaned_data['buysellvolume'])
		return redirect('index')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		if self.request.get_full_path() == '/':
			context['symbol'] = ''
		elif '?stockdata=' in self.request.get_full_path() and '?buysellvolume=' not in self.request.get_full_path():
			url = self.request.get_full_path()
			context['symbol'] = url.split('?stockdata=')[1]
		elif '?stockdata=' in self.request.get_full_path() and '?buysellvolume=' in self.request.get_full_path():
			url = self.request.get_full_path()
			context['volume'] = url.split('?buysellvolume=')[1]
		return context

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
