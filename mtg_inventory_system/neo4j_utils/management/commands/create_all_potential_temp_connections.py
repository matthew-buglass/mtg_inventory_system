import logging

from django.core.management.base import BaseCommand

from common.models import Card
from neo4j_utils.models import TempCardNodeConnection

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Creates Temp connections that don't exist"

    def handle(self, *args, **options):
        all_cards = Card.objects.all()
        all_temp_connections = TempCardNodeConnection.objects.all()
        card_pairs_to_create = []
        total_pairs = len(all_cards) ** 2
        examined_pairs = 0
        padding = len(f'{total_pairs:,}')

        logger.info(f'Examining {total_pairs:>{padding},} card pairs')
        for i in all_cards:
            for j in all_cards:
                if not all_temp_connections.filter(src_card=i, dst_card=j):
                    card_pairs_to_create.append(
                        TempCardNodeConnection(
                            src_card=i,
                            dst_card=j,
                            connection_type='triggers'
                        )
                    )
                examined_pairs += 1
                if examined_pairs % 1000 == 0:
                    logger.info(f'Examined {examined_pairs:>{padding},} card pairs')

        logger.info(f'Creating {len(card_pairs_to_create):,} temp connections')
        TempCardNodeConnection.objects.bulk_create(card_pairs_to_create)
