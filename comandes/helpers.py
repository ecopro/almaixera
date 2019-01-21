
from .models import *
from datetime import date, timedelta, datetime

# TODO: retornar llista de dates (generic) enlloc de tuples (pels combobox)

def recollida_tancada( data_recollida, coope ):
    recollides = [str(r[0]) for r in properes_comandes(coope)]
    if str(data_recollida)[:10] in recollides:
        return False
    return True

def properes_comandes( coope ):
    if not coope:
        return ()
    ara = datetime.now()
    conf = coope
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

# dates informe: totes les disponibles a la BBDD per una coope
def dates_informe( coope ):
    # TEST: filtrar les de una coope
    dates = Comanda.objects.filter(soci__cooperativa=coope).values('data_recollida').distinct().order_by('-data_recollida')
    llista = []
    for data in dates:
        d = data['data_recollida']
        llista.append( (str(d),str(d.day)+"/"+str(d.month)+"/"+str(d.year)) )
    return tuple( llista )
    #return [ (str(d['data_recollida']),str(d['data_recollida'])) for d in dates ]

def propera_recollida( coope ):
    if not coope:
        return None
    avui = date.today()
    conf = coope
    #dow_recollida = 1 #dimarts (p.ex)
    dow_recollida = conf.dow_recollida
    dow_tancament = conf.dow_tancament
    hora_tancament = conf.hora_tancament
    propera_recollida = dow_recollida - avui.weekday()
    if propera_recollida<=0:
        propera_recollida += 7
    return avui+timedelta(days=propera_recollida)

def propera_comanda( coope ):
    if not coope:
        return None
    dates = properes_comandes(coope)
    return dates[0][0]

def proper_tancament( coope ):
    if not coope:
        return None
    ara = datetime.now()
    avui = date.today()
    conf = coope
    dow_tancament = conf.dow_tancament
    hora_tancament = conf.hora_tancament
    proper_tanc = datetime.combine( avui + timedelta(dow_tancament-avui.weekday()) , hora_tancament )
    if proper_tanc < ara:
        proper_tanc += timedelta(7)
    return proper_tanc


def regenera_activacions( request ):
    # actualitzem activacions de proveidors i productes per la coope del coopeadmin que esta entrant
    coope = request.user.soci.cooperativa
    if coope:
        activacions_fetes = ActivaProveidor.objects.filter(cooperativa=coope)
        proveidors_fets = [ act.proveidor.id for act in activacions_fetes ]
        proveidors = Proveidor.objects.exclude( id__in=proveidors_fets )
        #debug
        #print("Generant activacions de proveidors: ",len(proveidors))
        # afegim proveidors que no s'han fet
        for prov in proveidors:
            activacio = ActivaProveidor(cooperativa=coope,proveidor=prov)
            activacio.actiu = False
            activacio.save()
        # afegim productes pendents d'afegir a tots els proveidors
        activacions = ActivaProveidor.objects.filter(cooperativa=coope)
        for activa_prov in activacions:
            activacions_fetes = ActivaProducte.objects.filter(
                        producte__proveidor=activa_prov.proveidor,cooperativa=coope )
            #print("Activacions fetes=",len(activacions_fetes))
            prods_fets = [ act.producte.id for act in activacions_fetes ]
            productes = Producte.objects.filter( proveidor=activa_prov.proveidor )
            productes = productes.exclude( id__in=prods_fets )
            #debug
            #print("Generant activacions de productes: ",len(productes))
            for prod in productes:
                activa_prod = ActivaProducte(producte=prod,cooperativa=coope,activa_proveidor=activa_prov)
                # TODO: exclude
                #activa_prod.actiu = False
                activa_prod.save()
    
