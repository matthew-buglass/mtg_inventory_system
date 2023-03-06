from django.test import TestCase

from common.models import Card
from neo4j_utils.models import CardNodeConnection, TempCardNodeConnection


class TestTempCardNodeConnection(TestCase):
    def setUp(self) -> None:
        pass

    def test_add_vote_for(self):
        pass

