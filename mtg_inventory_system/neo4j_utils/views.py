from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView

from neo4j_utils.models import CardNodeConnection, TempCardNodeConnection


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


def propose_connection_view(req, src_card, dst_card):
    pass


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
