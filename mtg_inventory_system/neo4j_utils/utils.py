import json
from typing import Callable

from django.db.models import QuerySet

from common.models import Card


def _remove_excess_quotes(query_string):
    return query_string.replace('{"', "{").replace('":', ':').replace(', "', ', ')


# Node Clauses
def create_node_clause(node_name: str, label: str, props: dict = None):
    create_str = f'CREATE ({node_name}:{label} {json.dumps(props)})'
    return _remove_excess_quotes(create_str)


# Relationship clauses
def create_relationship_clause(
        src_name: str,
        src_obj_type: str,
        dst_name: str,
        dst_obj_type: str,
        relation_type: str,
        relation_props: dict = None
):
    match_str = f"MATCH(a:{src_obj_type}),(b:{dst_obj_type})" \
                f"WHERE a.name = '{src_name}' AND b.name = '{dst_name}'" \
                f"CREATE (a)-[:{relation_type} {json.dumps(relation_props)}]->(b);"
    return _remove_excess_quotes(match_str)


def get_many_create_node_clause(
        objects: QuerySet,
        name_func: Callable[[object], str],
        label_func: Callable[[object], str],
        props_dict: Callable[[object], dict] = None
):
    return [
        create_node_clause(name_func(obj), label_func(obj), props_dict(obj)) if props_dict else
        create_node_clause(name_func(obj), label_func(obj))
        for obj in objects]


def get_many_relationship_clause(
        objects: QuerySet,
        src_name_func: Callable[[object], str],
        src_obj_type_func: Callable[[object], str],
        dst_name_func: Callable[[object], str],
        dst_obj_type_func: Callable[[object], str],
        relation_type_func: Callable[[object], str],
        props_func: Callable[[object], dict] = None
):
    return [
        create_relationship_clause(
            src_name_func(obj), src_obj_type_func(obj), dst_name_func(obj), dst_obj_type_func(obj),
            relation_type_func(obj), props_func(obj)) if props_func else
        create_relationship_clause(
            src_name_func(obj), src_obj_type_func(obj), dst_name_func(obj), dst_obj_type_func(obj),
            relation_type_func(obj))
        for obj in objects]
