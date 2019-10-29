from django.views.generic import TemplateView
from django.shortcuts import render
import requests

class IndexPageView(TemplateView):
	template_name = 'main/index.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['symbol'] = 'APPL'
		return context
	

class ChangeLanguageView(TemplateView):
	template_name = 'main/change_language.html'