from django.contrib import admin
from . import models


# Register your models here.
@admin.register(models.Reservatrion)
class ReservationAdmin(admin.ModelAdmin):

    """Reservation Admin Definition"""

    pass
