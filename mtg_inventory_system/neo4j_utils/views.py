import logging

from django.db.models import Q, Subquery, OuterRef
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, FormView, DetailView

from common.models import Card, CardFace
from neo4j_utils.froms import CreateTempCardNodeConnectionForm
from neo4j_utils.models import CardNodeConnection, TempCardNodeConnection


logger = logging.getLogger(__name__)


class ConnectionsListView(ListView):
    model = CardNodeConnection
    template_name = 'node_connection.html'
    paginate_by = 25

    def get_queryset(self):
        result = super(ConnectionsListView, self).get_queryset()
        query = self.request.GET.get('search')
        if query:
            post_result = result.filter(
                Q(src_card__name__icontains=query) |
                Q(dst_card__name__icontains=query))
            result = post_result
        return result


class TempConnectionsListView(ListView):
    model = TempCardNodeConnection
    template_name = 'node_connection.html'
    paginate_by = 25

    def get_queryset(self):
        result = super(TempConnectionsListView, self).get_queryset()
        query = self.request.GET.get('search')
        if query:
            post_result = result.filter(
                Q(src_card__name__icontains=query) |
                Q(dst_card__name__icontains=query))
            result = post_result
        return result


class PickSourceCardListView(ListView):
    model = Card
    template_name = 'connection_proposal/src_select.html'
    paginate_by = 25

    def get_queryset(self):
        result = super(PickSourceCardListView, self)\
            .get_queryset()\
            .get_cards_with_small_image_uri()\
            .order_by('name', 'card_set__name')\
            .distinct('name')
        query = self.request.GET.get('search')
        if query:
            post_result = result.filter(
                Q(name__icontains=query) |
                Q(cardface__type_line__icontains=query) |
                Q(cardface__oracle_text__icontains=query))
            result = post_result
        return result


class PickDestinationCardListView(ListView):
    model = Card
    template_name = 'connection_proposal/dst_select.html'
    paginate_by = 25

    def get_queryset(self):
        result = super(PickDestinationCardListView, self).get_queryset().exclude(pk=self.kwargs['pk'])\
            .get_cards_with_small_image_uri()\
            .exclude(pk=self.kwargs['pk'])\
            .order_by('name', 'card_set__name')\
            .distinct('name')
        query = self.request.GET.get('search')
        if query:
            post_result = result.filter(
                Q(name__icontains=query) |
                Q(cardface__type_line__icontains=query) |
                Q(cardface__oracle_text__icontains=query))
            result = post_result
        return result

    def get_context_data(self, **kwargs):
        result = super(PickDestinationCardListView, self).get_context_data(**kwargs)

        # General Card Details
        src_card = Card.objects.get_cards_with_small_image_uri(pk=self.kwargs['pk']).first()
        result['src_card'] = src_card

        return result


class ProposeConnectionFormView(FormView):
    form_class = CreateTempCardNodeConnectionForm
    template_name = 'forms/connection_view.html'
    success_url = '/connections/temp'

    def get_form(self, form_class=None):
        form = super(ProposeConnectionFormView, self).get_form(form_class)
        src_card = Card.objects.get_cards_with_small_image_uri(pk=self.kwargs['src_pk']).first()
        dst_card = Card.objects.get_cards_with_small_image_uri(pk=self.kwargs['dst_pk']).first()
        form.set_cards(src_card, dst_card)

        return form
    
    def form_valid(self, form):
        new_connection = TempCardNodeConnection(
            src_card=form.src_card,
            dst_card=form.dst_card,
            connection_type=form.cleaned_data['connection_type']
        )
        new_connection.save()
        return HttpResponseRedirect(self.get_success_url())


class ExportCardConnectionsToCypherView(ListView):
    model = CardNodeConnection
    template_name = 'node_connection.html'
    paginate_by = 25


def propose_connection_view(req):
    if req.method == 'POST':
        form = CreateTempCardNodeConnectionForm(req.POST)
        if form.is_valid():
            logger.info('form is valid')
    else:
        form = CreateTempCardNodeConnectionForm()

    return render(req, 'forms/connection_view.html', {'form': form})


def propose_connection(req, src_card, dst_card, connection_type):
    old_conn = TempCardNodeConnection.objects.get(
        src_card=src_card,
        dst_card=dst_card,
        connection_type=connection_type
    )

    # Make a new temp connection if one does not already exist
    if not old_conn:
        new_conn = TempCardNodeConnection(
            src_card=src_card,
            dst_card=dst_card,
            connection_type=connection_type
        )
        new_conn.save()


class VoteConnectionView(DetailView):
    model = TempCardNodeConnection
    template_name = 'vote_on_temp_node_connection.html'

    def get_context_data(self, **kwargs):
        result = super(VoteConnectionView, self).get_context_data(**kwargs)
        obj = result['object']
        result['votes_against'] = obj.total_votes - obj.votes_for

        return result


def insert_vote_on_connection(req, connection_id, connection_is_correct):
    conn = TempCardNodeConnection.objects.get(id=connection_id)
    print(connection_id, connection_is_correct)

    # Add a vote for/against
    if eval(connection_is_correct):
        conn.add_vote_for()
    else:
        conn.add_vote_against()

    # If we meet the threshold to establish the connection, create a permanent one and delete the temp one
    if conn.can_make_permanent():
        conn.make_permanent()
        conn.delete()

    return redirect('Vote on Connection', pk=connection_id)
