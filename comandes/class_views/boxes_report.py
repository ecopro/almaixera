import itertools
from datetime import datetime
from functools import wraps

from django.http import HttpResponseRedirect, JsonResponse
from django.views import View
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.forms.models import modelformset_factory
from django.forms import ModelForm
from django.db.models import Sum

from ..models import DetallComanda
from ..utils import unique, flatten, get_request_type

def membership_required(fn):
    @wraps(fn)
    def wrap(request, *args, **kwargs):
        current_user_is_soci = hasattr(request.user, 'soci')
        if current_user_is_soci:
            return fn(request, *args, **kwargs)
        else:
            return render(request, 'nosoci.html')
    return login_required(wrap)

class DetallComandaForm(ModelForm):
    error_css_class = 'data-error'

    class Meta:
        model = DetallComanda
        fields = ["quantitat_rebuda"]

def get_errors_from_formset(formset):
    format_error = lambda err: ["{}: {}".format(k, v) for (k, vs) in err.items() for v in vs]
    return unique(flatten(format_error(err) for err in formset.errors))

def get_sorted_details(date, coope):
    return (DetallComanda.objects.
        filter(
            comanda__data_recollida=date,
            comanda__soci__cooperativa=coope,
        ).order_by(
            'producte__nom',
            'producte__id',
            'comanda__soci__num_caixa',
        ))

def get_info(detall_comanda_id):
    detall = DetallComanda.objects.get(id=detall_comanda_id)
    user = detall.comanda.soci.user
    return dict(
        id=detall.id,
        num_caixa=detall.comanda.soci.num_caixa,
        soci="({}) {} {}".format(user.username, user.first_name, user.last_name),
        quant=detall.quantitat,
        preu=detall.producte.preu,
        subtotal=float(detall.quantitat_rebuda) * float(detall.producte.preu),
    )

def get_forms_by_product(formset, detalls):
    def get_product_from_form(form):
        detall_comanda_id = form["id"].value()
        detall_comanda = DetallComanda.objects.get(id=detall_comanda_id)
        return detall_comanda.producte

    def get_total(detalls, product):
        aggr = detalls.filter(producte__id=product.id).aggregate(Sum('quantitat'))
        return aggr["quantitat__sum"]

    def get_data(forms):
        return [dict(form=form, info=get_info(form['id'].value())) for form in forms]

    groups = itertools.groupby(formset, get_product_from_form)
    return [(product, get_total(detalls, product), get_data(forms)) for (product, forms) in groups]

def get_info_from_request(request):
    string_date = request.GET.get('data_informe')
    date = datetime.strptime(string_date, "%Y-%m-%d")
    cooperative = request.user.soci.cooperativa
    detalls = get_sorted_details(date, cooperative)
    FormsetClass = modelformset_factory(DetallComanda, form=DetallComandaForm, extra=0)
    return date, detalls, FormsetClass

def render_formset(request, date, formset, detalls):
    forms_by_product = get_forms_by_product(formset, detalls)
    string_date = datetime.strftime(date, "%Y-%m-%d")
    cooperative = request.user.soci.cooperativa
    errors = get_errors_from_formset(formset)
    return render(request, 'boxes_report.html', dict(
        old_form_url=reverse('informe_caixes') + "?data_informe=" + string_date,
        date=date,
        forms_by_product=forms_by_product,
        cooperative=cooperative,
        formset=formset,
        errors="\n".join(errors),
    ))

class BoxesReportView(View):
    @method_decorator(membership_required)
    def get(self, request):
        date, detalls, FormsetClass = get_info_from_request(request)
        formset = FormsetClass(queryset=detalls)
        return render_formset(request, date, formset, detalls)

    @method_decorator(membership_required)
    def post(self, request):
        date, detalls, FormsetClass = get_info_from_request(request)
        formset = FormsetClass(request.POST)

        if formset.is_valid():
            formset.save()
            if get_request_type(request) == "json":
                return JsonResponse(dict(success=True))
            else:
                return HttpResponseRedirect(request.get_full_path())
        else:
            if get_request_type(request) == "json":
                errors = get_errors_from_formset(formset)
                return JsonResponse(dict(success=False, errors=errors))
            else:
                return render_formset(request, date, formset, detalls)
