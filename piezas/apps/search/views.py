from django.core.files.storage import default_storage
from django.http import HttpResponse, Http404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, FormView, TemplateView, ListView
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse
from oscar.core.loading import get_model
import json
import forms
from piezas.apps.catalogue import models

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

                    if "quantity" in item:
                        initial_item['quantity'] = item['quantity']
                    else:
                        initial_item['quantity'] = 1
                    initial.append(initial_item)

            context['formset'] = forms.SearchCreationFormSet(initial=initial)
        return context
    
    def form_valid(self, form):
        response = super(HomeView, self).form_valid(form)
        context = self.get_context_data()
        formset = context['formset']

        final_data = {}
        final_data["engine"] = form.cleaned_data["engine"].id
        final_data["frameref"] = form.cleaned_data["frameref"]
        final_data["brand"] = form.cleaned_data["brand"].id
        final_data["version"] = form.cleaned_data["version"].id
        final_data["model"] = form.cleaned_data["model"].id
        final_data["bodywork"] = form.cleaned_data["bodywork"].id

        # formset
        final_data["pieces"] = []

        current_formset_data = formset.data
        max_item = int(current_formset_data['form-TOTAL_FORMS'])

        for i in range(max_item):
            final_item = {}
            prefix = "form-%s-" % i
            current_category = prefix+"category"
            current_piece = prefix+"piece"
            current_quantity = prefix+"quantity"
            current_comments = prefix+"comments"
            current_picture = prefix+"picture"

            if current_category in current_formset_data and current_formset_data[current_category] and \
                current_piece in current_formset_data and current_formset_data[current_piece]:

                final_item["category"] = current_formset_data[current_category]
                final_item["piece"] = current_formset_data[current_piece]
                final_item["comments"] = current_formset_data[current_comments]

                final_item["picture"] = current_formset_data[current_picture]

                if current_quantity in current_formset_data and current_formset_data[current_quantity]>0:
                    final_item["quantity"] = current_formset_data[current_quantity]
                else:
                    final_item["quantity"] = 1
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
                        print str(e)
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
            return HttpResponse(json.dumps({"result":False}), mimetype='application/json')


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

                search_request = models.SearchRequest(brand=brand, model=model,
                    version=version, bodywork=bodywork, engine=engine,
                    frameref=current_data["frameref"], comments=form.cleaned_data["comments"],
                    owner=self.request.user, expiration_date=form.cleaned_data['expiration_date'])
                search_request.save()

                # now create search items
                for piece in current_data["pieces"]:
                    category = models.Category.objects.get(pk=piece["category"])
                    piece_model = models.Product.objects.get(pk=piece["piece"])

                    search_request_item = models.SearchItemRequest(category=category,
                        piece=piece_model, comments=piece["comments"], quantity=piece["quantity"],
                        owner=self.request.user, search_request=search_request, state='pending',
                        picture=piece["picture"])
                    search_request_item.save()

                    # now create answers for these search items
                    questions = models.ProductQuestion.objects.filter(product=piece_model)
                    for question in questions:
                        question_key = 'question_'+str(question.id)
                        if question.type in ('text','boolean'):
                            answer = models.SearchItemRequestAnswers(search_item_request=search_request_item,
                                question=question)
                            if question.type=='text' and question_key in current_data:
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


class PendingSearchRequestsView(ListView):
    """
    Pending search requests
    """
    context_object_name = "searchrequests"
    template_name = 'search/pending_searchrequest_list.html'
    paginate_by = 20
    model = models.SearchRequest
    form_class = forms.SearchRequestSearchForm
    page_title = _('Active searches from customers')
    active_tab = 'searchrequests'

    def get(self, request, *args, **kwargs):
        if 'date_from' in request.GET:
            self.form = self.form_class(self.request.GET)
            if not self.form.is_valid():
                self.object_list = self.get_queryset()
                ctx = self.get_context_data(object_list=self.object_list)
                return self.render_to_response(ctx)
            data = self.form.cleaned_data
        else:
            self.form = self.form_class()
        return super(PendingSearchRequestsView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        qs = self.model._default_manager.filter(state='pending')
        if self.form.is_bound and self.form.is_valid():
            qs = qs.filter(**self.form.get_filters())
        return qs

    def get_context_data(self, *args, **kwargs):
        ctx = super(PendingSearchRequestsView, self).get_context_data(*args, **kwargs)
        ctx['form'] = self.form
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
        context['searchrequest'] = self.object
        return context
    
    def form_valid(self, form):
        response = super(QuoteView, self).form_valid(form)
        context = self.get_context_data()
        formset = context['formset']

        final_data = {}
        final_data["engine"] = form.cleaned_data["engine"].id
        final_data["frameref"] = form.cleaned_data["frameref"]
        final_data["brand"] = form.cleaned_data["brand"].id
        final_data["version"] = form.cleaned_data["version"].id
        final_data["model"] = form.cleaned_data["model"].id
        final_data["bodywork"] = form.cleaned_data["bodywork"].id

        # formset
        final_data["pieces"] = []

        if hasattr(formset, 'cleaned_data'):
            current_formset_data = formset.cleaned_data
            for current_item in current_formset_data:
                final_item = {}
                if "category" in current_item and current_item["category"] and \
                    "piece" in current_item and current_item["piece"]:
                    final_item["category"] = current_item["category"].id
                    final_item["piece"] = current_item["piece"].id
                    final_item["comments"] = current_item["comments"]

                    if "quantity" in current_item and current_item["quantity"]>0:
                        final_item["quantity"] = current_item["quantity"]
                    else:
                        final_item["quantity"] = 1

                    final_data["pieces"].append(final_item)   

            self.request.session['search_data'] = json.dumps(final_data)
            return True
        else:
            current_formset_data = formset.data
            max_item = int(current_formset_data['form-TOTAL_FORMS'])

            for i in range(max_item):
                final_item = {}
                prefix = "form-%s-" % i
                current_category = prefix+"category"
                current_piece = prefix+"piece"
                current_quantity = prefix+"quantity"
                current_comments = prefix+"comments"

                if current_category in current_formset_data and current_formset_data[current_category] and \
                    current_piece in current_formset_data and current_formset_data[current_piece]:
                    final_item["category"] = [current_formset_data[current_category],]
                    final_item["piece"] = [current_formset_data[current_category],]
                    final_item["comments"] = current_formset_data[current_category]

                    if current_quantity in current_formset_data and current_formset_data[current_quantity]>0:
                        final_item["quantity"] = current_formset_data[current_quantity]
                    else:
                        final_item["quantity"] = 1

                    final_data["pieces"].append(final_item)

            self.request.session['search_data'] = json.dumps(final_data)
            return True

    def get_success_url(self):
        return reverse('search:home')
