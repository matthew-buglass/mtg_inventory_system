from django.db.models import Model, JSONField, ForeignKey, CharField




class CardNodeConnection(Model):
    src_card = None
    dst_card =None
    connection_type =None
    connection_meta_data = JSONField(null=True)