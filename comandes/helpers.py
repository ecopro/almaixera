
from datetime import date, timedelta
from models import GlobalConf, Comanda


# TODO: retornar llista de dates (generic) enlloc de tuples (pels combobox)

def properes_dates_recollida():
    avui = date.today()

    conf = GlobalConf.objects.get()
    #dia_recollida = 1 #dimarts
    dia_recollida = conf.dow_recollida
    
    proper_dia = dia_recollida - avui.weekday()
    if proper_dia<=0:
        proper_dia += 7
    
    # TODO: posar x setmanes en global_conf
    # properes 4 setmanes
    llista = []
    for i in range(4):
        s = str(avui+timedelta(i*7+proper_dia))
        llista.append( (s,s) )
    
    return tuple(llista)


# dates informe: totes les disponibles a la BBDD
def dates_informe():
    dates = Comanda.objects.values('data_recollida').distinct().order_by('data_recollida')

    return [ (str(d['data_recollida']),str(d['data_recollida'])) for d in dates ]

def propera_recollida():
    avui = date.today()

    conf = GlobalConf.objects.get()
    dia_recollida = conf.dow_recollida

    proper_dia = dia_recollida - avui.weekday()
    if proper_dia<=0:
        proper_dia += 7

    return proper_dia
