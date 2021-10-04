from django.shortcuts import redirect, reverse
from django.views.generic import TemplateView
from django.contrib import messages
from rooms import models as room_models
from . import models as list_models


def toggle_room(request, pk):
    action = request.GET.get("action", None)
    room = room_models.Room.objects.get_or_none(pk=pk)
    if room is not None and action is not None:
        the_list, _ = list_models.List.objects.get_or_create(
            user=request.user, name="My Favorites Houses"
        )
        if action == "add":
            the_list.rooms.add(room)
            messages.success(request, "Saved to Favorites")
        elif action == "remove":
            the_list.rooms.remove(room)
            messages.success(request, "Removed from Favorites")

    return redirect(reverse("rooms:detail", kwargs={"pk": pk}))


class SeeFavsView(TemplateView):
    template_name = "lists/list_detail.html"
