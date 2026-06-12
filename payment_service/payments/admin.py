from django.contrib import admin

from payments.infrastructure.models import PaymentModel

admin.site.register(PaymentModel)
