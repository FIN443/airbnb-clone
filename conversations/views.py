from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, reverse, render
from django.views.generic import View
from users import mixins as user_mixins
from users import models as user_models
from . import models, forms


def go_conversation(request, host_pk, guest_pk):
    user_host = user_models.User.objects.get_or_none(pk=host_pk)
    user_guest = user_models.User.objects.get_or_none(pk=guest_pk)
    if user_host is not None and user_guest is not None:
        try:
            conversation = models.Conversation.objects.get(
                Q(participants=user_host) & Q(participants=user_guest)
            )
        except models.Conversation.DoesNotExist:
            conversation = models.Conversation.objects.create()
            conversation.participants.add(user_host, user_guest)
        return redirect(reverse("conversations:detail", kwargs={"pk": conversation.pk}))


class ConversationDetailView(user_mixins.LoggedInOnlyView, View):
    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        conversation = models.Conversation.objects.get_or_none(pk=pk)
        if not conversation:
            raise Http404()
        form = forms.AddCommentForm()
        return render(
            self.request,
            "conversations/conversation_detail.html",
            {"conversation": conversation, "form": form},
        )

    def post(self, *args, **kwargs):
        message = self.request.POST.get("message", None)
        pk = kwargs.get("pk")
        conversation = models.Conversation.objects.get_or_none(pk=pk)
        if not conversation:
            raise Http404()
        if message is not None:
            models.Message.objects.create(
                message=message,
                user=self.request.user,
                conversation=conversation,
            )
        return redirect(reverse("conversations:detail", kwargs={"pk": pk}))
