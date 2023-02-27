import django.db.models

from .utils import *


class CypherSerializer:
    def __init__(self):
        self.create_node_fn = create_node_clause
        self.create_relation_fn = create_relationship_clause

    def create_string(self, obj: django.db.models.Model, fields: dict):
        return self.create_node_fn(
            node_id=obj.id,
            label=obj.__class__.__name__,
            props=fields
        )

    def create_relation(
            self,
            src_obj: django.db.models.Model,
            dst_obj: django.db.models.Model,
            relation_type: str,
            relation_id: str = "",
            fields: dict = None
    ):
        return self.create_relation_fn(
            src_node_id=str(src_obj.id),
            dst_node_id=str(dst_obj.id),
            relation_type=relation_type.upper(),
            relation_id=relation_id,
            props=fields
        )
