import re

import django.db.models

from logging import getLogger

from django.forms import model_to_dict

from .models import CardNodeConnection
from .utils import *
from common.models import Card

logger = getLogger(__name__)


class CypherSerializerBase:
    def __init__(
            self,
            model_class,
            model_connection_class,
            create_node_fn=create_node_clause,
            create_relation_fn=create_relationship_clause,
            node_name_field='name',
            custom_fields=None
    ):
        if custom_fields is None:
            custom_fields = []

        self.create_node_fn = create_node_fn
        self.create_relation_fn = create_relation_fn
        self.model_class = model_class
        self.model_connection_class = model_connection_class
        self.fields = ['id'] + custom_fields
        self.node_name_field = node_name_field
        self.query_set = None

    def get_create_node_string(self, node_name: str,  obj: django.db.models.Model, fields: dict):
        return self.create_node_fn(
            node_name=node_name,
            label=obj.__class__.__name__,
            props={k: str(v) for k, v in fields.items()}
        )

    # def get_create_relation_string(
    #         self,
    #         src_obj: django.db.models.Model,
    #         dst_obj: django.db.models.Model,
    #         relation_type: str,
    #         relation_id: str = "",
    #         fields: dict = None
    # ):
    #     return self.create_relation_fn(
    #         src_node_id=str(src_obj.id),
    #         dst_node_id=str(dst_obj.id),
    #         relation_type=relation_type.upper(),
    #         relation_id=relation_id,
    #         props=fields
    #     )

    def _get_create_nodes_strings(self, query_set=None):
        create_strings_list = []
        if not query_set:
            query_set = self.query_set

        if query_set:
            for x in iter(query_set):
                fields = model_to_dict(x, fields=self.fields)
                create_strings_list.append(self.get_create_node_string(
                    node_name=str(model_to_dict(x)[self.node_name_field]).replace(' ', '_').lower(),
                    obj=x,
                    fields=fields
                ))

        logger.info(f'Got create string for {len(create_strings_list)} {self.model_class.__name__} nodes')
        return create_strings_list

    @staticmethod
    def _write_to_file(obj_type, file_name, cypher_list):
        if re.findall(r'\.cypher$', file_name):
            with open(file_name, 'w') as f:
                f.write('\n'.join(cypher_list))
                f.close()

            logger.info(f'Wrote create {obj_type} nodes to cypher file {file_name}')
        else:
            logger.error(f'No file writen, invalid file name `{file_name}`. Files must have a `.cypher` extension')


class CardCypherSerializer(CypherSerializerBase):
    def __init__(self):
        super(CardCypherSerializer, self).__init__(
            model_class=Card,
            model_connection_class=CardNodeConnection,
            custom_fields=['name', 'collector_number']
        )
        self.query_set = Card.objects.all().order_by('name', 'released_at').distinct('name')
