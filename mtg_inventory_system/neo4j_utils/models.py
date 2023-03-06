from django.db.models import Model, JSONField, ForeignKey, CharField, CASCADE, PositiveIntegerField

from .const import NODE_CONNECTION_TYPES
from .utils import *
from common.models import Card

VOTES_THRESHOLD = 15
VOTES_THRESHOLD_PERCENT = 0.75


class CardNodeConnection(Model):
    src_card = ForeignKey(Card, on_delete=CASCADE)
    dst_card = ForeignKey(Card, on_delete=CASCADE)
    connection_type = CharField(max_length=128, choices=NODE_CONNECTION_TYPES)
    connection_meta_data = JSONField(null=True)

    def cypher_string(self):
        return create_relationship_clause(
            src_props=,
            dst_props=,
            relation_type=,
            relation_props=
        )



class TempCardNodeConnection(Model):
    src_card = ForeignKey(Card, on_delete=CASCADE)
    dst_card = ForeignKey(Card, on_delete=CASCADE)
    connection_type = CharField(max_length=128, choices=NODE_CONNECTION_TYPES)
    connection_meta_data = JSONField(null=True)
    votes_for = PositiveIntegerField(default=0)
    total_votes = PositiveIntegerField(default=0)

    def _passes_vote_threshold(self):
        return self.total_votes >= VOTES_THRESHOLD

    def _passes_vote_percent_threshold(self):
        return (self.votes_for / self.total_votes) >= VOTES_THRESHOLD_PERCENT

    def can_make_permanent(self):
        return self._passes_vote_percent_threshold() and self._passes_vote_threshold()

    def make_permanent(self):
        connection = CardNodeConnection(
            src_card=self.src_card,
            dst_card=self.dst_card,
            connection_type=self.connection_type,
            connection_meta_data=self.connection_meta_data
        )
        connection.save()
