import logging

from django.core.management.base import BaseCommand

from ...cypher_serializers import CardCypherSerializer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Export the current card database to cypher for importing to Neo4j'

    def add_arguments(self, parser):
        parser.add_argument('--filename', type=str)

    def handle(self, *args, **options):
        filename = options.get('filename') or 'cards.cypher'

        serializer = CardCypherSerializer()
        serializer.write_create_all_nodes_string_to_file(filename)
