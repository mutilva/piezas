from django.core.files.storage import default_storage
from django.http import HttpResponse, Http404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, FormView, TemplateView, ListView, DetailView, View
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse
from oscar.core.loading import get_model
from oscar.apps.order.models import Line, BillingAddress, ShippingAddress
from piezas.apps.order.models import Order
from oscar.apps.partner.models import Partner
from datetime import datetime
import math
from dateutil import tz
import json
import forms
from piezas import settings
from piezas.apps.catalogue import models
from django.contrib.sites.models import Site

class HomeView(FormView):
    form_class = forms.SearchCreationForm
    template_name = 'search/home.html'
    dupes_message = _("Duplicate products aren't allowed")

    def get_form_kwargs(self):
        current_session = self.request.session.get('search_data', None)
        if current_session:
            current_data = json.loads(current_session)
            kwargs = {'data':current_data}
            kwargs.update(super(HomeView, self).get_form_kwargs())
        else:
            kwargs = super(HomeView, self).get_form_kwargs()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = forms.SearchCreationFormSet(self.request.POST)
        else:
            current_session = self.request.session.get('search_data', None)
            initial = []
            if current_session:
                current_data = json.loads(current_session)
                for item in current_data['pieces']:
                    initial_item = {}
                    initial_item['category'] = item['category']
                    initial_item['piece'] = item['piece']
                    initial_item['comments'] = item['comments']
                    initial_item['picture'] = item['picture']

                    initial.append(initial_item)

            context['formset'] = forms.SearchCreationFormSet(initial=initial)
        return context
    
    def form_valid(self, form):
        response = super(HomeView, self).form_valid(form)
        context = self.get_context_data()
        formset = context['formset']

        final_data = {}
        final_data["name"] = form.cleaned_data["name"]
        final_data["engine"] = form.cleaned_data["engine"].id
        final_data["frameref"] = form.cleaned_data["frameref"]
        final_data["brand"] = form.cleaned_data["brand"].id
        final_data["version"] = form.cleaned_data["version"].id
        final_data["model"] = form.cleaned_data["model"].id
        final_data["bodywork"] = form.cleaned_data["bodywork"].id

        final_data["picture1"] = form.cleaned_data["picture1"]
        final_data["picture2"] = form.cleaned_data["picture2"]
        final_data["picture3"] = form.cleaned_data["picture3"]
        final_data["picture4"] = form.cleaned_data["picture4"]
        final_data["picture5"] = form.cleaned_data["picture5"]
        final_data["picture6"] = form.cleaned_data["picture6"]
        final_data["picture7"] = form.cleaned_data["picture7"]
        final_data["picture8"] = form.cleaned_data["picture8"]
        final_data["picture9"] = form.cleaned_data["picture9"]
        final_data["picture10"] = form.cleaned_data["picture10"]

        # formset
        final_data["pieces"] = []

        current_formset_data = formset.data
        max_item = int(current_formset_data['form-TOTAL_FORMS'])

        for i in range(max_item):
            final_item = {}
            prefix = "form-%s-" % i
            current_category = prefix+"category"
            current_piece = prefix+"piece"
            current_comments = prefix+"comments"
            current_picture = prefix+"picture"

            if current_category in current_formset_data and current_formset_data[current_category] and \
                current_piece in current_formset_data and current_formset_data[current_piece]:

                final_item["category"] = current_formset_data[current_category]
                final_item["piece"] = current_formset_data[current_piece]
                final_item["comments"] = current_formset_data[current_comments]

                final_item["picture"] = current_formset_data[current_picture]

                final_data["pieces"].append(final_item)

        # questions
        for key,val in self.request.POST.items():
            if key.startswith('question_'):
                final_data[key] = val
        self.request.session['search_data'] = json.dumps(final_data)
        return True

    def get_success_url(self):
        return reverse('search:home')

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        is_valid = form.is_valid()

        # first check if we have dupes of pieces
        current_pieces = []
        for key, val in request.POST.items():
            if key.endswith('-piece') and val:
                if val not in current_pieces:
                    current_pieces.append(val)
                    form_container = key.replace('-piece', '')
                    photo_container = form_container+'-picture'

                    # get product questions
                    try:
                        questions = models.ProductQuestion.objects.filter(product=val)
                        for question in questions:
                            if question.type == 'text':
                                # check if we have a value supplied
                                question_key = 'question_'+str(question.id)
                                if question_key not in request.POST or not request.POST[question_key]:
                                    # error
                                    return HttpResponse(json.dumps({"result":False, "error_message":unicode(_('Please fill all mandatory questions'))}), mimetype='application/json')
                            elif question.type == 'photo':
                                # check if we have included a picture
                                if photo_container not in request.POST or not request.POST[photo_container]:
                                    # error
                                    return HttpResponse(json.dumps({"result":False, "error_message":unicode(_('Please include all mandatory pictures'))}), mimetype='application/json')

                    except Exception as e:
                        pass

                else:
                    # error
                    return HttpResponse(json.dumps({"result":False, "error_message":unicode(self.dupes_message)}), mimetype='application/json')
        if is_valid:
            # check that all the questions have values
            result = self.form_valid(form)
            return HttpResponse(json.dumps({"result":result}), mimetype='application/json')
        else:
            self.form_invalid(form)
            return HttpResponse(json.dumps({"result":False, "error_message": unicode(_('Please fill all mandatory fields'))}), mimetype='application/json')


class ConfirmView(FormView):
    form_class = forms.SearchConfirmForm
    template_name = 'search/confirm.html'

    def get_context_data(self, **kwargs):
        context = super(ConfirmView, self).get_context_data(**kwargs)

        # retrieve data from session
        current_session = self.request.session.get('search_data', None)
        if current_session:
            current_data = json.loads(current_session)
            if 'brand' in current_data:
                current_data['brand_name'] = models.Brand.objects.get(pk=current_data['brand']).name
            if 'model' in current_data:
                current_data['model_name'] = models.Model.objects.get(pk=current_data['model']).name
            if 'version' in current_data:
                current_data['version_name'] = models.Version.objects.get(pk=current_data['version']).name
            if 'bodywork' in current_data:
                current_data['bodywork_name'] = models.Bodywork.objects.get(pk=current_data['bodywork']).name
            if 'engine' in current_data:
                current_data['engine_name'] = models.Engine.objects.get(pk=current_data['engine']).name
            context['search_data'] = current_data

            for piece in current_data["pieces"]:
                if 'category' in piece:
                    piece['category_name'] = models.Category.objects.get(pk=piece['category'])
                if 'piece' in piece:
                    piece['piece_name'] = models.Product.objects.get(pk=piece['piece'])

                # get the questions for each piece
                questions = models.ProductQuestion.objects.filter(product=piece['piece'])
                piece['questions'] = []
                for question in questions:
                    question_data = {}
                    question_data['type'] = question.type
                    question_data['text'] = question.text
                    question_key = 'question_'+str(question.id)
                    if question_key in current_data:
                        question_data['value'] = current_data[question_key]
                    else:
                        question_data['value'] = ''
                    piece['questions'].append(question_data)
        return context

    def form_valid(self, form):
        response = super(ConfirmView, self).form_valid(form)
        current_session = self.request.session.get('search_data', None)
        if current_session:
            current_data = json.loads(current_session)

            try:
                # create search objects
                brand = models.Brand.objects.get(pk=current_data["brand"])
                model = models.Model.objects.get(pk=current_data["model"])
                version = models.Version.objects.get(pk=current_data["version"])
                bodywork = models.Bodywork.objects.get(pk=current_data["bodywork"])
                engine = models.Engine.objects.get(pk=current_data["engine"])

                # get user default shipping address
                address = self.request.user.get_default_shipping_address()
                if address is not None:
                    longitude = address.longitude
                    latitude = address.latitude
                else:
                    longitude = latitude = None

                search_request = models.SearchRequest(name=current_data["name"], brand=brand, model=model,
                    version=version, bodywork=bodywork, engine=engine,
                    frameref=current_data["frameref"], comments=form.cleaned_data["comments"],
                    owner=self.request.user, longitude=longitude, latitude=latitude,
                    picture1=current_data['picture1'],
                    picture2=current_data['picture2'],
                    picture3=current_data['picture3'],
                    picture4=current_data['picture4'],
                    picture5=current_data['picture5'],
                    picture6=current_data['picture6'],
                    picture7=current_data['picture7'],
                    picture8=current_data['picture8'],
                    picture9=current_data['picture9'],
                    picture10=current_data['picture10'],
                    )
                search_request.save()

                # now create search items
                for piece in current_data["pieces"]:
                    category = models.Category.objects.get(pk=piece["category"])
                    piece_model = models.Product.objects.get(pk=piece["piece"])

                    search_request_item = models.SearchItemRequest(category=category,
                        piece=piece_model, comments=piece["comments"],
                        owner=self.request.user, search_request=search_request, state='pending',
                        picture=piece["picture"])
                    search_request_item.save()

                    # now create answers for these search items
                    questions = models.ProductQuestion.objects.filter(product=piece_model)
                    for question in questions:
                        question_key = 'question_'+str(question.id)
                        if question.type in ('text','boolean','list'):
                            answer = models.SearchItemRequestAnswers(search_item_request=search_request_item,
                                question=question)
                            if question.type in ('text','list') and question_key in current_data:
                                answer.text_answer = current_data[question_key]
                            else:
                                answer.boolean_answer = (question_key in current_data)
                            answer.save()

                # clear session
                del(self.request.session['search_data'])

            except Exception as e:
                print str(e)
        return response


    def get_success_url(self):
        return reverse('search:placed')


class PlacedView(TemplateView):
    template_name = 'search/placed.html'

class QuotePlacedView(TemplateView):
    template_name = 'search/quoteplaced.html'

class OrderPlacedView(TemplateView):
    template_name = 'search/orderplaced.html'


class PendingSearchRequestsView(ListView):
    """
    Pending search requests
    """
    context_object_name = "searchrequests"
    template_name = 'search/pending_searchrequest_list.html'
    paginate_by = 20
    model = models.SearchRequest
    page_title = _('Active searches from customers')
    active_tab = 'searchrequests'

    def get_queryset(self):
        # get user lat and long
        user_address = self.request.user.get_default_shipping_address()
        if user_address:
            current_latitude = user_address.latitude
            current_longitude = user_address.longitude

            #1- Aquellas Busquedas realizadas por Talleres de <100Km y realizadas en las ultimas 3h
            #2- Aquellas Busquedas realizadas por Talleres de [200Km 500km] y que lleven activas entre 1:30h y 3h
            #3- Aquellas Busquedas realizadas por Talleres de [500Km 1000km] y que lleven activas entre 3:00h y 4:30h
            #4- Aquellas Busquedas realizadas por Talleres de [1000km] y que lleven activas entre 4:30h y 6h
            qs = self.model.objects.raw("""
            select catalogue_searchrequest.*,
            earth_distance(ll_to_earth(latitude,longitude),ll_to_earth(%f,%f)) as distance
            from catalogue_searchrequest where state = %s and 
            id not in (select search_request_id from catalogue_quote where owner_id = %s) and 
            (
                (earth_box( ll_to_earth(%f, %f), %d) @> ll_to_earth(latitude, longitude)
                 and date_created between (current_timestamp - interval '%d min') and current_timestamp) or 
                (earth_box( ll_to_earth(%f, %f), %d) @> ll_to_earth(latitude, longitude)
                 and date_created between (current_timestamp - interval '%d min') and 
                 (current_timestamp - interval '%d min')) or
                (earth_box( ll_to_earth(%f, %f), %d) @> ll_to_earth(latitude, longitude)
                 and date_created between (current_timestamp - interval '%d min') and 
                 (current_timestamp - interval '%d min')) or
                (earth_box( ll_to_earth(%f, %f), %d) @> ll_to_earth(latitude, longitude)
                 and date_created between (current_timestamp - interval '%d min') and 
                 (current_timestamp - interval '%d min'))
            )
            """ % (current_latitude, current_longitude, "'pending'", self.request.user.id,
                   current_latitude, current_longitude, 100000, (settings.SEARCH_INTERVAL_MIN*2),
                   current_latitude, current_longitude, 200000, (settings.SEARCH_INTERVAL_MIN*3), settings.SEARCH_INTERVAL_MIN,
                   current_latitude, current_longitude, 500000, (settings.SEARCH_INTERVAL_MIN*4), (settings.SEARCH_INTERVAL_MIN*3),
                   current_latitude, current_longitude, 1000000, (settings.SEARCH_INTERVAL_MIN*5), (settings.SEARCH_INTERVAL_MIN*4),
                ))
            items = list(qs)
            for item in items:
                # get zone
                current_time = datetime.utcnow()
                creation_date = item.date_created.astimezone(tz.tzutc()).replace(tzinfo=None)
                time_diff = current_time - creation_date

                search_user = item.owner
                address = search_user.get_default_shipping_address()
                if address:
                    item.zone = u'%s - %s' % (address.postcode, address.state)
                final_distance = item.distance/1000
                if final_distance<100:
                    item.search_type = _('Regional')
                    item.remaining_time = (2*settings.SEARCH_INTERVAL_MIN*60) - time_diff.total_seconds()
                elif final_distance<200:
                    item.search_type = _('Bordering')
                    item.remaining_time = (3*settings.SEARCH_INTERVAL_MIN*60) - time_diff.total_seconds()
                elif final_distance<500:
                    item.remaining_time = (4*settings.SEARCH_INTERVAL_MIN*60) - time_diff.total_seconds()
                    item.search_type = _('Supraregional')
                else:
                    item.remaining_time = (5*settings.SEARCH_INTERVAL_MIN*60) - time_diff.total_seconds()
                    item.search_type = _('Regional')

                mins = math.floor(item.remaining_time/60)
                secs = math.floor(item.remaining_time - (mins*60))
                item.remaining_time = "%d:%02d" % (mins, secs)
            return items
        else:
            return []

    def get_context_data(self, *args, **kwargs):
        ctx = super(PendingSearchRequestsView, self).get_context_data(*args, **kwargs)
        return ctx

class QuoteView(UpdateView):
    form_class = forms.QuoteCreationForm
    template_name = 'search/quote.html'
    model = models.SearchRequest

    def get_context_data(self, *args, **kwargs):
        context = super(QuoteView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = forms.InlineQuoteCreationFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = forms.InlineQuoteCreationFormSet(instance=self.object)

        for form in context['formset'].forms:
            try:
                form.initial['category'] = models.Category.objects.get(pk=form.initial['category'])
            except Exception as e:
                 pass

            try:
                form.initial['piece'] = models.Product.objects.get(pk=form.initial['piece'])
            except:
                pass

            if 'answers' not in form.initial:
                try:
                    search_item = models.SearchItemRequest.objects.get(pk=form.initial['id'])
                    answers_text = u''
                    for answer in search_item.answers:
                        answers_text += u'%s: '% answer.question.text
                        if answer.question.type == 'boolean':
                            if answer.boolean_answer:
                                answers_text += unicode(_('Yes'))
                            else:
                                answers_text += unicode(_('No'))
                        else:
                            answers_text += answer.text_answer
                        answers_text += u'\n'

                    form.initial['answers'] = answers_text
                except Exception as e:
                    pass

        # get zone
        search_user = self.object.owner
        address = search_user.get_default_shipping_address()
        if address:
            self.object.zone = u'%s - %s' % (address.postcode, address.state)
        context['searchrequest'] = self.object
        return context

    def form_valid(self, form):
        response = super(QuoteView, self).form_valid(form)

        request_id = form.initial['id']
        warranty_days = form.cleaned_data['warranty_days']
        shipping_days = form.cleaned_data['shipping_days']
        shipping_total_excl_tax = form.cleaned_data['shipping_total_excl_tax']
        quote_comments = form.cleaned_data['quote_comments']
        base_total = 0
        
        total_forms = form.data['searchitemrequest_set-TOTAL_FORMS']
        items = []
        for i in range(int(total_forms)):
            data_item = {}
            quantity = form.data['searchitemrequest_set-%d-quantity' % i]
            if int(quantity) > 0:
                data_item['id'] = form.data['searchitemrequest_set-%d-id' % i]
                data_item['picture'] = form.data['searchitemrequest_set-%d-quote_picture' % i]
                data_item['line_total'] = form.data['searchitemrequest_set-%d-base_total' % i]
                data_item['line_comments'] = form.data['searchitemrequest_set-%d-quote_comments' % i]
                base_total += float(data_item['line_total'])
                items.append(data_item)

        # calc totals
        shipping_total_incl_tax = float(shipping_total_excl_tax) + float(shipping_total_excl_tax*settings.TPC_TAX/100)
        grand_total_excl_tax = float(base_total) + float(shipping_total_excl_tax)
        base_total_incl_tax = float(base_total) + float(base_total*settings.TPC_TAX/100)
        grand_total_incl_tax = float(base_total_incl_tax) + float(shipping_total_incl_tax)

        # create entries
        try:
            search_request = models.SearchRequest.objects.get(pk=request_id)
            quote = models.Quote(search_request=search_request, owner=self.request.user,
                                 state='sent', base_total_excl_tax=base_total,
                                 base_total_incl_tax=base_total_incl_tax,
                                 shipping_total_excl_tax=shipping_total_excl_tax,
                                 shipping_total_incl_tax=shipping_total_incl_tax,
                                 grand_total_excl_tax=grand_total_excl_tax,
                                 grand_total_incl_tax=grand_total_incl_tax,
                                 comments=quote_comments, warranty_days=warranty_days,
                                 shipping_days=shipping_days)
            quote.save()

            for item in items:
                # create quote item
                request_item = models.SearchItemRequest.objects.get(pk=item['id'])
                quoteitem = models.QuoteItem(quote=quote, search_item_request=request_item,
                                             owner=self.request.user, base_total_excl_tax=item['line_total'],
                                             state='sent', comments=item['line_comments'],
                                             picture=item['picture'])
                quoteitem.save()

        except Exception as e:
            print str(e)
            return False

        return response

    def get_success_url(self):
        return reverse('search:quoteplaced')


class ActiveQuotesView(ListView):
    """
    View active quotes for that customer
    """
    context_object_name = "quotes"
    template_name = 'search/activequotes_list.html'
    paginate_by = 20
    model = models.Quote
    page_title = _('Active quotes')
    active_tab = 'quotes'

    def get_queryset(self):
        # only show quotes for searches that belong to user
        queryset = models.Quote.objects.filter(search_request__owner=self.request.user, state='sent')
        return queryset


class SearchDetailView(DetailView):
    model = models.SearchRequest
    context_object_name = 'searchrequest'
    template_name = 'search/detail.html'
    searchrequest_actions = ()

    def get_object(self, queryset=None):
        return models.SearchRequest.objects.get(id=self.kwargs['number'])


class QuoteDetailView(DetailView):
    model = models.Quote
    context_object_name = 'quote'
    template_name = 'search/quotedetail.html'
    quote_actions = ()

    def get_context_data(self, *args, **kwargs):
        context = super(QuoteDetailView, self).get_context_data(**kwargs)
        context['tpc_tax'] = settings.TPC_TAX

        return context

    def get_object(self, queryset=None):
        return models.Quote.objects.get(id=self.kwargs['number'])

class QuoteAcceptView(DetailView):
    model = models.Quote
    context_object_name = 'quote'
    template_name = 'search/quoteaccept.html'
    quote_actions = ()

    def get_context_data(self, *args, **kwargs):
        lines = self.request.GET.get('lines', '')
        line_items = []
        line_ids = []
        base_total = 0
        for line in lines.split(','):
            quote_line = models.QuoteItem.objects.get(id=line)
            line_items.append(quote_line)
            line_ids.append('%s' % quote_line.id)
            base_total += quote_line.base_total_excl_tax

        context = super(QuoteAcceptView, self).get_context_data(**kwargs)
        context['lines'] = line_items
        context['line_ids'] = ','.join(line_ids)

        quote = kwargs['object']
        context['base_total_excl_tax'] = base_total
        context['base_total_incl_tax'] = float(base_total) + float(base_total*settings.TPC_TAX/100)
        context['shipping_total_excl_tax'] = quote.shipping_total_excl_tax
        context['shipping_total_incl_tax'] = quote.shipping_total_incl_tax
        context['grand_total_excl_tax'] = float(base_total) + float(context['shipping_total_excl_tax'])
        context['grand_total_incl_tax'] = float(context['base_total_incl_tax']) + float(context['shipping_total_incl_tax'])

        return context

    def get_object(self, queryset=None):
        return models.Quote.objects.get(id=self.kwargs['number'])


class RecalcQuoteView(View):
    def post(self, request, *args, **kwargs):
        quote_id = request.POST.get('quote_id', '')
        line_ids = request.POST.get('ids', '').split(',')

        # mark the quote for recalc, mark the lines as accepted
        response_data = {}
        if line_ids and len(line_ids)>0:
            quote = models.Quote.objects.get(pk=quote_id)
            if quote:
                quote.state = 'pending_recalc'
                quote.save()

                # mark all the lines as accepted or rejected
                lines = models.QuoteItem.objects.filter(quote=quote)
                for line in lines:
                    if unicode(line.id) in line_ids:
                        line.state = 'accepted'
                    else:
                        line.state = 'rejected'
                    line.save()
                response_data['result'] = 'OK'
            else:
                response_data['result'] = 'KO'
                response_data['error'] = _('We cannot find your quote. Please try again.')
        else:
            response_data['result'] = 'KO'
            response_data['error'] = _('There has been an error processing your request. Please try again.')

        return HttpResponse(json.dumps(response_data), content_type="application/json")

class RecalcPlacedView(TemplateView):
    template_name = 'search/recalcplaced.html'

class PlaceOrderView(View):
    def post(self, request, *args, **kwargs):
        quote_id = request.POST.get('quote_id', '')
        line_ids = request.POST.get('ids', '').split(',')
        payment_method = request.POST.get('payment_method', 'payondelivery')

        quote = models.Quote.objects.get(pk=quote_id)
        response_data = {}
        if quote and line_ids and len(line_ids)>0:
            base_total = 0
            for line_id in line_ids:
                line = models.QuoteItem.objects.get(pk=line_id)
                base_total += line.base_total_excl_tax

            # create order
            order = Order()
            order.number = quote.id
            order.user = request.user
            order.site = Site.objects.get_current()
                
            order.currency = 'EUR'
            order.status = 'pending_payment'

            # get totals
            order.total_excl_tax = base_total
            order.total_incl_tax = float(base_total) + float(base_total*settings.TPC_TAX/100)
            order.shipping_excl_tax = quote.shipping_total_excl_tax
            order.shipping_incl_tax = quote.shipping_total_incl_tax

            # payment method
            order.payment_method = payment_method
            if payment_method == 'transfer':
                order.bank_account = quote.owner.iban
            order.save()

            # create order lines
            for line_id in line_ids:
                order_line = Line()
                order_line.order = order
                line = models.QuoteItem.objects.get(pk=line_id)

                # check if owner is partner, if not, create it
                try:
                    partner = Partner.objects.get(code=quote.owner.cif)
                except:
                    partner = Partner()
                    partner.code = quote.owner.cif
                    partner.name = quote.owner.commercial_name
                    partner.save()
                    
                order_line.partner = partner
                order_line.partner_name = quote.owner.commercial_name
                order_line.partner_sku = quote.owner.cif
                order_line.title = line.search_item_request
                order_line.upc = line.search_item_request.id
                order_line.product = line.search_item_request.piece
                order_line.quantity = 1

                order_line.unit_price_excl_tax = line.base_total_excl_tax
                order_line.line_price_excl_tax = line.base_total_excl_tax
                order_line.line_price_incl_tax = float(line.base_total_excl_tax) + float(line.base_total_excl_tax*settings.TPC_TAX/100)

                order_line.line_price_before_discounts_incl_tax = float(line.base_total_excl_tax) + float(line.base_total_excl_tax*settings.TPC_TAX/100)
                order_line.line_price_before_discounts_excl_tax = line.base_total_excl_tax
                order_line.save()
                

            # create addresses
            shipping_address = ShippingAddress()
            shipping_address.__dict__ = request.user.get_default_shipping_address().__dict__
            shipping_address.save()
            order.shipping_address = shipping_address

            # get user address
            billing_address = BillingAddress()
            if request.user.get_default_billing_address():
                billing_address.__dict__ = request.user.get_default_billing_address().__dict__
            else:
                billing_address.__dict__ = request.user.get_default_shipping_address().__dict__
            billing_address.save()
            order.billing_address = billing_address
            order.save()

            # associate order with quote
            quote.order = order
            quote.state = 'accepted'
            quote.save()

            # mark all the lines as accepted or rejected
            lines = models.QuoteItem.objects.filter(quote=quote)
            for line in lines:
                if line.id in line_ids:
                    line.state = 'accepted'
                else:
                    line.state = 'rejected'
                line.save()
            response_data['result'] = 'OK'
        else:
            response_data['result'] = 'KO'
            response_data['error'] = _('There has been an error processing your request. Please try again.')

        return HttpResponse(json.dumps(response_data), content_type="application/json")

class RecalcQuotesView(ListView):
    """
    View active quotes for that customer
    """
    context_object_name = "quotes"
    template_name = 'search/recalcquotes_list.html'
    paginate_by = 20
    model = models.Quote
    page_title = _('Quotes pending from shipping recalc')
    active_tab = 'quotes'

    def get_queryset(self):
        # only show quotes for searches that belong to user
        queryset = models.Quote.objects.filter(owner=self.request.user, state='pending_recalc')
        return queryset

class QuoteRecalcView(DetailView):
    model = models.Quote
    context_object_name = 'quote'
    template_name = 'search/confirmquoterecalc.html'
    quote_actions = ()

    def get_object(self, queryset=None):
        return models.Quote.objects.get(id=self.kwargs['number'])

    def get_context_data(self, *args, **kwargs):
        quote = kwargs['object']
        lines = quote.accepted_lines
        base_total = 0
        for quote_line in lines:
            base_total += quote_line.base_total_excl_tax

        context = super(QuoteRecalcView, self).get_context_data(**kwargs)
        context['base_total_excl_tax'] = base_total
        context['base_total_incl_tax'] = float(base_total) + float(base_total*settings.TPC_TAX/100)
        context['shipping_total_excl_tax'] = quote.shipping_total_excl_tax
        context['shipping_total_incl_tax'] = quote.shipping_total_incl_tax
        context['grand_total_excl_tax'] = float(base_total) + float(context['shipping_total_excl_tax'])
        context['grand_total_incl_tax'] = float(context['base_total_incl_tax']) + float(context['shipping_total_incl_tax'])

        return context
