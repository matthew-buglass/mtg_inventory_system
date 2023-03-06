from django.test import TestCase

from common.factories import CardFactory
from neo4j_utils.models import CardNodeConnection, TempCardNodeConnection


class TestTempCardNodeConnection(TestCase):
    def setUp(self) -> None:
        self.src_card = CardFactory()
        self.dst_card = CardFactory()

    def test_add_vote_for(self):
        self.assertEqual(self.src_card, self.dst_card)

