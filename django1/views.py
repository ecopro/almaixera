# Create your views here.

from django.http import HttpResponse

def home(request):
    return HttpResponse("""
	Benvinguts a l'Almaixera.<br>
	Realitza la teva <a href="/comandes">comanda</a>.
""")
    
    
