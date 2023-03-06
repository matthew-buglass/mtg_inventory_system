import json


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
