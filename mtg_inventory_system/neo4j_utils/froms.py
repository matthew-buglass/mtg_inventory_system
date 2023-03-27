from django.forms import ModelChoiceField, ChoiceField, Form

from common.models import Card
from neo4j_utils.const import NODE_CONNECTION_TYPES


class CreateTempCardNodeConnectionForm(Form):
    src_card = ModelChoiceField(required=True, queryset=Card.objects.filter(name__icontains='enlighten'), empty_label='Triggering Card')
    dst_card = ModelChoiceField(required=True, queryset=Card.objects.filter(name__icontains='enlighten'), empty_label='Triggered Card')
    connection_type = ChoiceField(required=True, choices=NODE_CONNECTION_TYPES)


