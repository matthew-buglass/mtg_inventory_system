import json


# Node Clauses
def create_node_clause(node_id, label: str, props: dict = None):
    return f'CREATE ({node_id}:{label} {json.dumps(props)})'


# Relationship clauses
def create_relationship_clause(src_node_id, dst_node_id, relation_type: str, relation_id: str = "", props: dict = None):
    return f'CREATE ({src_node_id})-[{relation_id}:{relation_type} {json.dumps(props)}]->({dst_node_id})'
