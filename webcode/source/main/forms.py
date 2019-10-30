from datetime import timedelta

from django import forms
from django.forms import ValidationError
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.db.models import Q
from django.utils.translation import gettext_lazy as _



class StocksForm(forms.Form):
    #password = forms.CharField(label=_('Password'), strip=False, widget=forms.PasswordInput)

    stockdata = forms.CharField(label = _('StockName'), strip=False, max_length=500 )

    def get_data(self):
        stock_data = self.cleaned_data['stockdata']
        ''' par = {'symbol':'SNAP', 'api_token':'svaMvA7fFajd6B3EBsfrLZL6lCfmqLl6vJgCbGPBisqN74QPzH3kF49JDqR4'}
        response = requests.get(url = 'https://api.worldtradingdata.com/api/v1/stock', params = par)
        if response.status_code == 200:
            result = response.json()
            result['success'] = True
        else:
            result['success'] = False
            if response.status_code == 404:
                result['message'] = "NOT FOUND"
            else:
               result['message'] = "WORLDTRADINGDATA API IS NOT AVAILABLE AT THE MOMENT. PLEASE TRY AGAIN LATER."
        '''
        return stock_data