from django.contrib import admin
from .models import User, Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_method', 'payment_date')
    list_filter = ('payment_method', 'payment_date')
