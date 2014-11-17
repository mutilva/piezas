# Only define custom UserManager/UserModel when Django >= 1.5
from django.contrib.auth import models as auth_models
from django.core.exceptions import ValidationError
from django.db import models
from django_iban.fields import IBANField
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from piezas.apps.address.models import UserAddress
import re

TYPE_CHOICES = (
    ('customer', _('Workshop')),
    ('provider', _('Scrapping'))
)

def validate_phone_number(value):
    result = re.match(r'^\+?(\d{7,15})$', value)
    if result is None or not result:
        raise ValidationError(_('%s is not a valid phone number') % value)


if hasattr(auth_models, 'BaseUserManager'):

    class UserManager(auth_models.BaseUserManager):

        def create_user(self, email, password=None, **extra_fields):
            """
            Creates and saves a User with the given username, email and
            password.
            """
            now = timezone.now()
            if not email:
                raise ValueError('The given email must be set')
            email = UserManager.normalize_email(email)
            user = self.model(
                email=email, is_staff=False, is_active=True,
                is_superuser=False,
                last_login=now, date_joined=now, **extra_fields)

            user.set_password(password)
            user.save(using=self._db)
            return user

        def create_superuser(self, email, password, **extra_fields):
            u = self.create_user(email, password, **extra_fields)
            u.is_staff = True
            u.is_active = True
            u.is_superuser = True
            u.save(using=self._db)
            return u


    class PiezasUser(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
        email = models.EmailField(_('email address'), unique=True)
        commercial_name = models.CharField(
            _('Commercial name'), max_length=255, blank=True)
        social_name = models.CharField(
            _('Social name'), max_length=255, blank=False)
        first_name = models.CharField(
            _('First name'), max_length=255, blank=True)
        last_name = models.CharField(
            _('Last name'), max_length=255, blank=True)
        is_staff = models.BooleanField(
            _('Staff status'), default=False,
            help_text=_('Designates whether the user can log into this admin '
                        'site.'))
        is_active = models.BooleanField(
            _('Active'), default=True,
            help_text=_('Designates whether this user should be treated as '
                        'active. Unselect this instead of deleting accounts.'))
        is_validated = models.BooleanField(
            _('Validated'), default=True,
            help_text=_('Designates if the user has been validated by admins and has full access to platform.'))
        type = models.CharField(_('Customer type'), choices=TYPE_CHOICES, max_length=15, default='customer')
        cif = models.CharField(_('CIF'), max_length=9)
        promotional_code = models.CharField(_('Promotional code'), max_length=50, blank=True, null=True)
        contact_person = models.CharField(
            _('Contact person'), max_length=255, blank=False)
        phone_number = models.CharField(_("Contact phone"), blank=False, max_length=255,
            help_text=_("In case we need to call you"), validators=[validate_phone_number])
        iban = IBANField(_('Bank number account (IBAN format)'), blank=True, null=True)
        date_joined = models.DateTimeField(_('date joined'),
                                           default=timezone.now)

        objects = UserManager()

        USERNAME_FIELD = 'email'

        class Meta:
            verbose_name = _('User')
            verbose_name_plural = _('Users')
        def get_full_name(self):
            full_name = '%s %s' % (self.first_name, self.last_name)
            return full_name.strip()

        def get_short_name(self):
            return self.first_name

        def _migrate_alerts_to_user(self):
            """
            Transfer any active alerts linked to a user's email address to the
            newly registered user.
            """
            ProductAlert = self.alerts.model
            alerts = ProductAlert.objects.filter(
                email=self.email, status=ProductAlert.ACTIVE)
            alerts.update(user=self, key=None, email=None)

        def get_full_name(self):
            full_name = '%s %s' % (self.first_name, self.last_name)
            return full_name.strip()

        def get_short_name(self):
            return self.first_name

        def _migrate_alerts_to_user(self):
            """
            Transfer any active alerts linked to a user's email address to the
            newly registered user.
            """
            ProductAlert = self.alerts.model
            alerts = ProductAlert.objects.filter(
                email=self.email, status=ProductAlert.ACTIVE)
            alerts.update(user=self, key=None, email=None)

        # given an user, return the default shipping address
        def get_default_shipping_address(self):
            try:
                address = UserAddress.objects.get(user=self, is_default_for_shipping=True)
                return address
            except Exception as e:
                return None

        # given an user, return the default billing address
        def get_default_billing_address(self):
            try:
                address = UserAddress.objects.get(user=self, is_default_for_billing=True)
                return address
            except Exception as e:
                return None
