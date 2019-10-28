from django.views.generic import TemplateView
from django.shortcuts import render
import requests

class IndexPageView(TemplateView):
	template_name = 'main/index.html'

	def home(request):
		par = {'symbol':'SNAP', 'api_token':'svaMvA7fFajd6B3EBsfrLZL6lCfmqLl6vJgCbGPBisqN74QPzH3kF49JDqR4'}
		response = requests.get(url = 'https://api.worldtradingdata.com/api/v1/stock', params = par)
		stock = response.json() if response and response.status_code == 200 else None
		if stock and 'symbol' in stock:
			dic = json.loads(stock)
			return render(request, 'main/home.html', dic['data'][0])


class ChangeLanguageView(TemplateView):
	template_name = 'main/change_language.html'