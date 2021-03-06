from django.db import models
from django.utils.translation import ugettext as _
from oscar.apps.catalogue.abstract_models import AbstractProduct as AbstractProduct
from oscar.apps.catalogue.models import ProductImage
from oscar.core.compat import AUTH_USER_MODEL
from smart_selects.db_fields import ChainedForeignKey
from oscar.apps.catalogue.models import Category
from oscar.apps.order.models import Order

from datetime import datetime
import math
from dateutil import tz
from piezas import settings

class BrandManager(models.Manager):

    def base_queryset(self):
        """
        Return ``QuerySet`` with related content pre-loaded.
        """
        return self.get_query_set().all()


class Brand(models.Model):
    name = models.CharField(_('Car brand'), max_length=255)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date Updated"), auto_now=True, db_index=True)
    objects = BrandManager()

    def __unicode__(self):
        return self.name


class ModelManager(models.Manager):

    def base_queryset(self):
        """
        Return ``QuerySet`` with related content pre-loaded.
        """
        return self.get_query_set().all()


class Model(models.Model):
    brand = models.ForeignKey(Brand, verbose_name = _('Car brand'))
    name = models.CharField(_('Car model'), max_length=255)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date Updated"), auto_now=True, db_index=True)
    objects = ModelManager()

    def __unicode__(self):
        return self.name


class VersionManager(models.Manager):

    def base_queryset(self):
        """
        Return ``QuerySet`` with related content pre-loaded.
        """
        return self.get_query_set().all()


class Version(models.Model):
    model = models.ForeignKey(Model, verbose_name = _('Car model'))
    name = models.CharField(_('Car version'), max_length=255)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date Updated"), auto_now=True, db_index=True)
    objects = VersionManager()

    def __unicode__(self):
        return self.name


class EngineManager(models.Manager):

    def base_queryset(self):
        """
        Return ``QuerySet`` with related content pre-loaded.
        """
        return self.get_query_set().all()


class Engine(models.Model):
    version = models.ForeignKey(Version, verbose_name = _('Car version'))
    name = models.CharField(_('Car engine'), max_length=255)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date Updated"), auto_now=True, db_index=True)
    objects = EngineManager()

    def __unicode__(self):
        return self.name

class BodyworkManager(models.Manager):

    def base_queryset(self):
        """
        Return ``QuerySet`` with related content pre-loaded.
        """
        return self.get_query_set().all()


class Bodywork(models.Model):
    name = models.CharField(_('Car bodywork type'), max_length=255)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date Updated"), auto_now=True, db_index=True)
    objects = BodyworkManager()

    def __unicode__(self):
        return self.name


class Product(AbstractProduct):
    pass


QUESTION_TYPES = (('boolean', _('Boolean')), ('text', _('Text')), ('photo', _('Photo')),
                  ('list', _('Option list')))

class ProductQuestion(models.Model):
    text = models.CharField(_('Product question'), max_length=255)
    type = models.CharField(_('Question type'), max_length=25, choices=QUESTION_TYPES,
        default='boolean')
    options = models.TextField(_('List of options, separated by pipes'), blank=True)
    
    product = models.ForeignKey(Product, verbose_name=_("Piece"),
        help_text=_('Piece to ask for'), related_name='product_question')

    def __unicode__(self):
        return self.text


SEARCH_REQUEST_STATES = (('pending', _('pending')), ('expired', _('expired')),
    ('canceled', _('canceled')))

class SearchRequest(models.Model):
    brand = models.ForeignKey(Brand, verbose_name=_("Brand"),
        blank=True, null=True, related_name='product_brand')
    other_brand = models.CharField(_('Other brand'), max_length=255, blank=True, null=True)
    model = ChainedForeignKey(Model, chained_field="brand", chained_model_field="brand",
        show_all=False, auto_choose=False, verbose_name=_("Car model"),
        help_text=_('Model of the car that it belongs to'), blank=True, null=True,
        related_name='product_model')
    other_model = models.CharField(_('Other model'), max_length=255, blank=True, null=True)
    version = ChainedForeignKey(Version, chained_field="model", chained_model_field="model",
        show_all=False, auto_choose=True, verbose_name=_("Car version"),
        help_text=_('Version of the car that it belongs to'), blank=True, null=True,
        related_name='product_version')
    other_version = models.CharField(_('Other version'), max_length=255, blank=True, null=True)
    bodywork = models.ForeignKey(Bodywork, verbose_name=_("Bodywork type"),
        blank=True, null=True, related_name='product_bodywork')
    other_bodywork = models.CharField(_('Other bodywork'), max_length=255, blank=True, null=True)
    engine = models.ForeignKey(Engine, verbose_name=_("Car engine"),
        blank=True, null=True, related_name='product_engine')
    other_engine = models.CharField(_('Other engine'), max_length=255, blank=True, null=True)
    frameref = models.CharField(_('Frame reference'), max_length=255, blank=True, null=True)
    comments = models.TextField(_('Comments'), blank=True)
    name = models.CharField(_('Search name'), max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date Updated"), auto_now=True, db_index=True)
    owner = models.ForeignKey(
        AUTH_USER_MODEL, related_name='search_requests', null=True,
        verbose_name=_("Owner"))
    state = models.CharField(max_length=25, choices=SEARCH_REQUEST_STATES, default='pending')
    latitude = models.DecimalField(_('Latitude'), max_digits=40, decimal_places=20)
    longitude = models.DecimalField(_('Longitude'), max_digits=40, decimal_places=20)

    picture1 = models.CharField(max_length=255, blank=True, null=True)
    picture2 = models.CharField(max_length=255, blank=True, null=True)
    picture3 = models.CharField(max_length=255, blank=True, null=True)
    picture4 = models.CharField(max_length=255, blank=True, null=True)
    picture5 = models.CharField(max_length=255, blank=True, null=True)
    picture6 = models.CharField(max_length=255, blank=True, null=True)
    picture7 = models.CharField(max_length=255, blank=True, null=True)
    picture8 = models.CharField(max_length=255, blank=True, null=True)
    picture9 = models.CharField(max_length=255, blank=True, null=True)
    picture10 = models.CharField(max_length=255, blank=True, null=True)

    @property
    def lines(self):
        items = SearchItemRequest.objects.filter(search_request=self)
        return items

    @property
    def num_items(self):
        return self.lines.count()        

    @property
    def quotes(self):
        items = Quote.objects.filter(search_request=self)
        return items

    @property
    def num_quotes(self):
        return self.quotes.count()

    @property
    def accepted_quotes(self):
        return self.quotes.filter(state='accepted').count()

    @property
    def zone(self):
        if self.state == 'pending':
            current_time = datetime.utcnow()
            creation_date = self.date_created.astimezone(tz.tzutc()).replace(tzinfo=None)
            time_diff = current_time - creation_date

            if time_diff.total_seconds() < 2*settings.SEARCH_INTERVAL_MIN*60:
                return _('Regional')
            elif time_diff.total_seconds() < 3*settings.SEARCH_INTERVAL_MIN*60:
                return _('Bordering')
            elif time_diff.total_seconds() < 4*settings.SEARCH_INTERVAL_MIN*60:
                return _('Supraregional')
            elif time_diff.total_seconds() < 5*settings.SEARCH_INTERVAL_MIN*60:
                return _('National')
            else:
                return u'-'
        else:
            return u'-'

    def distance_from_point(self, latitude, longitude):
        qs = SearchRequest.objects.raw("""
            SELECT id, earth_distance(ll_to_earth( %f, %f ), ll_to_earth(latitude, longitude)) as distance
            FROM catalogue_searchrequest WHERE id=%d
        """ % (latitude, longitude, self.id))
        if len(list(qs))>0:
            item = list(qs)[0]
            return item.distance
        else:
            return None

    def has_valid_distance(self, user):
        # no valid zone
        if self.zone == '-':
            return False

        user_address = user.get_default_shipping_address()
        if not user_address:
            return False

        # now calculate the distance between the search request and our point
        if self.zone == _('Regional'):
            start_distance = 0
            end_distance = 100000
        elif self.zone == _('Bordering'):
            start_distance = 100000
            end_distance = 200000
        elif self.zone == _('Supraregional'):
            start_distance = 200000
            end_distance = 500000
        elif self.zone == _('National'):
            start_distance = 500000
            end_distance = 1000000

        distance = self.distance_from_point(user_address.latitude, user_address.longitude)
        if distance is not None:
            if distance>=start_distance and distance<=end_distance:
                return True
        return False


class SearchItemRequest(models.Model):
    category = models.ForeignKey(Category, verbose_name=_('Category'),
        help_text=_('Category to search for'), related_name='product_category')
    piece = models.ForeignKey(Product, verbose_name=_("Piece"), help_text=_('Piece to search for'), related_name='product_piece')
    comments = models.TextField(_('Comments'), blank=True)
    quantity = models.PositiveIntegerField(_('Quantity'), default=1)
    picture = models.ImageField(upload_to='searchpictures/', blank=True)

    owner = models.ForeignKey(
        AUTH_USER_MODEL, related_name='search_product_requests', null=True,
        verbose_name=_("Owner"))
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date Updated"), auto_now=True, db_index=True)
    search_request = models.ForeignKey(SearchRequest, verbose_name = _('Search request'), blank=True, null=True)
    state = models.CharField(max_length=25, choices=SEARCH_REQUEST_STATES, default='pending')

    def __unicode__(self):
        return u'%s - %s - %s' % (self.category, self.piece, self.comments)

    @property
    def answers(self):
        try:
            items = SearchItemRequestAnswers.objects.filter(search_item_request=self.id)
        except Exception as e:
            print str(e)
        return items


class SearchItemRequestAnswers(models.Model):
    search_item_request = models.ForeignKey(SearchItemRequest, verbose_name = _('Search item request'), blank=True, null=True)
    question = models.ForeignKey(ProductQuestion, verbose_name=_('Piece question'), help_text=_('Question associated to piece'), related_name='piece_question')
    boolean_answer = models.NullBooleanField(_('Answer for boolean types'), blank=True, null=True)
    text_answer = models.TextField(_('Answer for text types'), blank=True, null=True)
    image_answer = models.ImageField(upload_to='media/searchpictures/', blank=True, null=True)

    owner = models.ForeignKey(
        AUTH_USER_MODEL, related_name='search_answers', null=True,
        verbose_name=_("Owner"))
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date Updated"), auto_now=True, db_index=True)

    def __unicode__(self):
        if self.question.type == 'boolean':
            if self.boolean_answer:
                return u'%s - %s' % (self.question.text, _('Yes'))
            else:
                return u'%s - %s' % (self.question.text, _('No'))
        elif self.question.type == 'text' or self.question_type == 'list':
            return u'%s - %s' % (self.question.text, self.text_answer)
        else:
            return u'%s - %s' % (self.question.text, _('Image'))


QUOTE_STATES = (('sent', _('Sent')), ('accepted', _('accepted')),
    ('pending_recalc', _('Pending from recalc')),
    ('partially_accepted', _('Partially accepted')), ('rejected', _('Rejected')),
    ('expired', _('Expired')))


class Quote(models.Model):
    search_request = models.ForeignKey(SearchRequest, verbose_name = _('Associated search request'), blank=False)
    owner = models.ForeignKey(
        AUTH_USER_MODEL, related_name='quote_owner', null=True,
        verbose_name=_("Owner"))
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date Updated"), auto_now=True, db_index=True)
    date_accepted = models.DateTimeField(_("Date Accepted"), null=True, blank=True)
    date_recalc = models.DateTimeField(_("Date Recalculated"), null=True, blank=True)
    state = models.CharField(max_length=25, choices=QUOTE_STATES, default='pending')
    base_total_excl_tax = models.DecimalField(_('Base total excluding tax'), decimal_places=2, max_digits=12)
    base_total_incl_tax = models.DecimalField(_('Base total including tax'), decimal_places=2, max_digits=12)
    shipping_total_excl_tax = models.DecimalField(_('Shipping total excluding tax'), decimal_places=2, max_digits=12)
    shipping_total_incl_tax = models.DecimalField(_('Shipping total including tax'), decimal_places=2, max_digits=12)
    grand_total_excl_tax = models.DecimalField(_('Grand total excluding tax'), decimal_places=2, max_digits=12)
    grand_total_incl_tax = models.DecimalField(_('Grand total including tax'), decimal_places=2, max_digits=12)
    comments = models.TextField(_('Comments'), blank=True)
    warranty_days = models.PositiveIntegerField(_('Warranty days'), blank=True, null=True)
    shipping_days = models.PositiveIntegerField(_('Shipping days'), blank=True, null=True)
    order = models.ForeignKey(Order, verbose_name = _('Associated order'), blank=True, null=True)

    @property
    def lines(self):
        items = QuoteItem.objects.filter(quote=self)
        return items

    @property
    def accepted_lines(self):
        items = QuoteItem.objects.filter(quote=self, state='accepted')
        return items

    @property
    def num_items(self):
        return self.lines.count()        

    @property
    def num_accepted_items(self):
        return self.accepted_lines.count()


QUOTE_ITEM_STATES = (('sent', _('Sent')), ('accepted', _('Accepted')),
    ('rejected', _('Rejected')))

class QuoteItem(models.Model):
    quote = models.ForeignKey(Quote, verbose_name = _('Associated quote'), blank=False)
    search_item_request = models.ForeignKey(SearchItemRequest, verbose_name = _('Associated search request item'), blank=False)
    owner = models.ForeignKey(
        AUTH_USER_MODEL, related_name='quote_item_owner', null=True,
        verbose_name=_("Owner"))
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date Updated"), auto_now=True, db_index=True)
    quantity = models.PositiveIntegerField(_('Quantity'), default=1)
    base_total_excl_tax = models.DecimalField(_('Base total excluding tax'), decimal_places=2, max_digits=12)
    state = models.CharField(max_length=25, choices=QUOTE_ITEM_STATES, default='pending')
    comments = models.TextField(_('Comments'), blank=True)
    picture = models.ImageField(upload_to='searchpictures/', blank=True, null=True)

class PromotionalCodeManager(models.Manager):

    def base_queryset(self):
        """
        Return ``QuerySet`` with related content pre-loaded.
        """
        return self.get_query_set().all()

class PromotionalCode(models.Model):
    code = models.CharField(_('Promotional code'), max_length=100)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date Updated"), auto_now=True, db_index=True)
    objects = PromotionalCodeManager()

    def __unicode__(self):
        return self.code

