from django.db.models import Model, JSONField, ForeignKey, CharField

from common.models import Card


class CardNodeConnection(Model):
    src_card = ForeignKey(Card)
    dst_card =
    connection_type =
    connection_meta_data = JSONField(null=True)