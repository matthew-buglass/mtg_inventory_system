import logging

from django.db.models import Q, Subquery, OuterRef
from django.shortcuts import render
from django.views.generic import ListView

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
    template_name = 'connection_proposal/src_select.html'
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
        result['src_card'] = {
            'name': src_card.name,
            'image_uri': src_card.card_img,
        }

        return result


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


def vote_on_connection(req, connection_id, connection_is_correct):
    conn = TempCardNodeConnection.objects.get(id=connection_id)

    # Add a vote for/against
    if connection_is_correct:
        conn.add_vote_for()
    else:
        conn.add_vote_against()

    # If we meet the threshold to establish the connection, create a permanent one and delete the temp one
    if conn.can_make_permanent():
        conn.make_permanent()
        conn.delete()
