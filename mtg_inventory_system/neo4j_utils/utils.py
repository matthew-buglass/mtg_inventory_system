import json


def _remove_excess_quotes(query_string):
    return query_string.replace('{"', "{").replace('":', ':').replace(', "', ', ')


# Node Clauses
def create_node_clause(node_name: str, label: str, props: dict = None):
    create_str = f'CREATE ({node_name}:{label} {json.dumps(props)})'
    return _remove_excess_quotes(create_str)


# Relationship clauses
def create_relationship_clause(src_props: dict, dst_props: dict, relation_type: str, relation_props: dict = None):
    """
    Example:
        MATCH(a:Card),(b:Card)WHERE a.name = 'Bile Blight' AND b.name = 'Treefolk Seedlings'CREATE (a)-[:TRIGGERS {name: a.name + '->' + b.name}]->(b);
        MATCH(a:Card),(b:Card)WHERE a.name = 'Treefolk Seedlings' AND b.name = 'Bile Blight'CREATE (a)-[:TRIGGERS {name: a.name + '->' + b.name}]->(b);
    """
    return f'CREATE (n:{src_props})-[:{relation_type} {json.dumps(relation_props)}]->({dst_props})'
