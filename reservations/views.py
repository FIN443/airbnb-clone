import datetime
from django.http import Http404
from django.views.generic import View, ListView
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from users import mixins as user_mixins
from rooms import models as room_models
from reviews import forms as review_forms
from . import models


class CreateError(Exception):
    pass


def create(request, room, year, month, day):
    try:
        date_obj = datetime.datetime(year, month, day)
        room = room_models.Room.objects.get(pk=room)
        models.BookedDay.objects.get(day=date_obj, reservation__room=room)
        raise CreateError()
    except (room_models.Room.DoesNotExist, CreateError):
        messages.error(request, "Can't Reserve that Room!")
        return redirect(reverse("core:home"))
    except models.BookedDay.DoesNotExist:
        reservation = models.Reservatrion.objects.create(
            guest=request.user,
            room=room,
            check_in=date_obj,
            check_out=date_obj + datetime.timedelta(days=1),
        )
        return redirect(reverse("reservations:detail", kwargs={"pk": reservation.pk}))


class ReservationDetailView(user_mixins.LoggedInOnlyView, View):
    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        reservation = models.Reservatrion.objects.get_or_none(pk=pk)
        if not reservation or (
            reservation.guest != self.request.user
            and reservation.room.host != self.request.user
        ):
            raise Http404()
        form = review_forms.CreateReviewForm()
        return render(
            self.request,
            "reservations/detail.html",
            {"reservation": reservation, "form": form},
        )


def edit_reservation(request, pk, verb):
    reservation = models.Reservatrion.objects.get_or_none(pk=pk)
    if not reservation or (
        reservation.guest != request.user and reservation.room.host != request.user
    ):
        raise Http404()
    if verb == "confirm":
        reservation.status = models.Reservatrion.STATUS_CONFIRMED
    elif verb == "cancel":
        reservation.status = models.Reservatrion.STATUS_CANCELED
        models.BookedDay.objects.filter(reservation=reservation).delete()
    reservation.save()
    messages.success(request, "Reservation Updated!")
    return redirect(reverse("reservations:detail", kwargs={"pk": reservation.pk}))


class ReservationGuestView(user_mixins.LoggedInOnlyView, ListView):
    model = models.Reservatrion
    template_name = "reservations/list.html"
    context_object_name = "reservations"

    def get(self, request, *args, **kwargs):
        user = request.user
        object_list = self.get_queryset()
        self.object_list = object_list.filter(guest=user)
        allow_empty = self.get_allow_empty()
        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(
                self.object_list, "exists"
            ):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(
                    _("Empty list and “%(class_name)s.allow_empty” is False.")
                    % {
                        "class_name": self.__class__.__name__,
                    }
                )
        context = self.get_context_data()
        return self.render_to_response(context)


class ReservationHostView(user_mixins.LoggedInOnlyView, ListView):
    pass
