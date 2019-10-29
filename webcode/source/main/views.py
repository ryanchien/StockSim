from django.views.generic import TemplateView
from django.shortcuts import render
import accounts.forms
import requests

class IndexPageView(TemplateView):
    template_name = 'main/index.html'

    def stocks(request):
    	stocks_result = form.get_stocks()
    	return render(request, 'main/index.html', {'form': form, 'stocks_result': stocks_result})

class ChangeLanguageView(TemplateView):
    template_name = 'main/change_language.html'
