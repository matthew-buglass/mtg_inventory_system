import re

import django.db.models

from logging import getLogger

from .utils import *
from ..common.models import Card

logger = getLogger(__name__)


class CypherSerializerBase:
    def __init__(
            self,
            model_class,
            create_node_fn=create_node_clause,
            create_relation_fn=create_relationship_clause,
            fields=None
    ):
        if fields is None:
            fields = []

        self.create_node_fn = create_node_fn
        self.create_relation_fn = create_relation_fn
        self.model_class = model_class
        self.fields = fields

    def get_create_node_string(self, obj: django.db.models.Model, fields: dict):
        return self.create_node_fn(
            node_id=obj.id,
            label=obj.__class__.__name__,
            props=fields
        )

    def get_create_relation_string(
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

    def get_create_all_nodes_string(self):
        create_strings_list = []
        if self.model_class:
            objects = self.model_class.objects.all()
            for x in iter(objects):
                fields = x.values(*self.fields)
                create_strings_list.append(self.get_create_node_string(
                    obj=x,
                    fields=fields
                ))

        logger.info(f'Got create string for {len(create_strings_list)} {self.model_class.__name__} nodes')
        return '\n'.join(create_strings_list)

    def write_create_all_nodes_string_to_file(self, file_name):
        if re.match(r'\.cypher?', file_name):
            with open(file_name, 'w') as f:
                f.write(self.get_create_all_nodes_string())
                f.close()

            logger.info(f'Wrote create {self.model_class.__name__} nodes to cypher file {file_name}')
        else:
            logger.error(f'No file writen, invalid file name {file_name}. Files must have a `.cypher` extension')


class CardCypherSerializer(CypherSerializerBase):
    def __init__(self):
        super(CardCypherSerializer, self).__init__(model_class=Card, fields=['name', 'collector_number'])
