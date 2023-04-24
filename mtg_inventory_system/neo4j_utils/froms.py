from django.forms import ModelChoiceField, ChoiceField, Form

from common.models import Card
from neo4j_utils.const import NODE_CONNECTION_TYPES


class CreateTempCardNodeConnectionForm(Form):
    connection_type = ChoiceField(required=True, choices=NODE_CONNECTION_TYPES)
    src_card = None
    dst_card = None

    def set_cards(self, src_card, dst_card):
        self.src_card = src_card
        self.dst_card = dst_card
