
from datetime import date, timedelta, datetime
from models import GlobalConf, Comanda


# TODO: retornar llista de dates (generic) enlloc de tuples (pels combobox)

def recollida_tancada( data_recollida ):
    ara = datetime.now()
    conf = GlobalConf.objects.get()
    dow_tancament = conf.dow_tancament
    incr_tancament = dow_tancament - ara.weekday()
    if incr_tancament<=0:
        incr_tancament += 7
    data_tancament = ara + timedelta(incr_tancament)
    # si arriba data tancament passem a la seguent setmana
    if type(data_recollida) == date:
        data_recollida = datetime.combine( data_recollida, datetime.min.time() )
    if data_tancament > data_recollida:
        return True
    return False


def properes_comandes():
    ara = datetime.now()
    conf = GlobalConf.objects.get()
    #dow_recollida = 1 #dimarts (p.ex)
    dow_recollida = conf.dow_recollida
    dow_tancament = conf.dow_tancament
    hora_tancament = conf.hora_tancament
    propera_recollida = dow_recollida - ara.weekday()
    if propera_recollida<=0:
        propera_recollida += 7
    proper_tancament = dow_tancament - ara.weekday()
    if proper_tancament<0:
        proper_tancament += 7
    # si arriba data tancament passem a la seguent setmana
    if proper_tancament > propera_recollida or \
        (proper_tancament==0 and ara.time()>hora_tancament):
        propera_recollida += 7
    # properes n setmanes
    n = conf.num_setmanes_previsio
    llista = []
    for i in range(n):
        data = ara.date()+timedelta(i*7+propera_recollida)
        llista.append( (str(data), str(data.day)+" / "+str(data.month)) )
    return tuple(llista)


# dates informe: totes les disponibles a la BBDD
def dates_informe():
    dates = Comanda.objects.values('data_recollida').distinct().order_by('data_recollida')
    llista = []
    for data in dates:
        d = data['data_recollida']
        llista.append( (str(d),str(d.day)+"/"+str(d.month)+"/"+str(d.year)) )
    return tuple( llista )
    #return [ (str(d['data_recollida']),str(d['data_recollida'])) for d in dates ]

