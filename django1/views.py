# Create your views here.

from django.http import HttpResponse
from django import http

def home(request):
	return http.HttpResponseRedirect('comandes')
