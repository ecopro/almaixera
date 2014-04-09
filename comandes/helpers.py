
from datetime import date, timedelta

def properes_dates_recollida():
    avui = date.today()

    # TODO: posar dimarts/dia_recollida en global_conf
    dia_recollida = 1 #dimarts
    
    proper_dia = dia_recollida - avui.weekday()
    if proper_dia<0:
        proper_dia += 7
    
    # TODO: posar x setmanes en global_conf
    # properes 4 setmanes
    llista = []
    for i in range(4):
        s = str(avui+timedelta(i*7+proper_dia))
        llista.append( (s,s) )
    
    return tuple(llista)
