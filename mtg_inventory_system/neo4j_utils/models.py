from django.db.models import Model, JSONField, ForeignKey, CharField, CASCADE, PositiveIntegerField

from .const import NODE_CONNECTION_TYPES
from .utils import *
from common.models import Card

VOTES_THRESHOLD = 15
VOTES_THRESHOLD_PERCENT = 0.75


class CardNodeConnection(Model):
    src_card = ForeignKey(Card, on_delete=CASCADE, related_name='src_card')
    dst_card = ForeignKey(Card, on_delete=CASCADE, related_name='dst_card')
    connection_type = CharField(max_length=128, choices=NODE_CONNECTION_TYPES)
    connection_meta_data = JSONField(null=True)

    def cypher_string(self):
        return create_relationship_clause(
            src_name=self.src_card.name,
            src_obj_type=Card.__name__,
            dst_name=self.dst_card.name,
            dst_obj_type=Card.__name__,
            relation_type=str(self.connection_type),
            relation_props=self.connection_meta_data
        )


class TempCardNodeConnection(Model):
    src_card = ForeignKey(Card, on_delete=CASCADE, related_name='src_card_temp')
    dst_card = ForeignKey(Card, on_delete=CASCADE, related_name='dst_card_temp')
    connection_type = CharField(max_length=128, choices=NODE_CONNECTION_TYPES)
    connection_meta_data = JSONField(null=True)
    votes_for = PositiveIntegerField(default=0)
    total_votes = PositiveIntegerField(default=0)

    def _passes_vote_threshold(self):
        return self.total_votes >= VOTES_THRESHOLD

    def _passes_vote_percent_threshold(self):
        return (self.votes_for / self.total_votes) >= VOTES_THRESHOLD_PERCENT

    def add_vote_for(self):
        self.votes_for += 1
        self.total_votes += 1

    def add_vote_against(self):
        self.total_votes += 1

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
