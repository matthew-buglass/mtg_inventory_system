from django.test import TestCase

from neo4j_utils.factories import CardNodeConnectionFactory, TempCardNodeConnectionFactory
from neo4j_utils.models import VOTES_THRESHOLD, VOTES_THRESHOLD_PERCENT


class TestCardNodeConnection(TestCase):

    def test_add_vote_for(self):
        expected_string = "MATCH(a:Card),(b:Card)WHERE a.name = 'src_card' AND b.name = 'dst_card'CREATE (a)-[:triggers {}]->(b);"

        node_connection = CardNodeConnectionFactory(
            src_card__name='src_card',
            dst_card__name='dst_card',
        )

        result_string = node_connection.cypher_string()
        print(result_string)
        self.assertEqual(expected_string, result_string)


class TestTempCardNodeConnection(TestCase):
    def test_under_votes_threshold_does_not_pass_threshold_test(self):
        temp_node_connection = TempCardNodeConnectionFactory(
            total_votes=VOTES_THRESHOLD-1
        )

        self.assertFalse(temp_node_connection._passes_vote_threshold())

    def test_at_votes_threshold_does_pass_threshold_test(self):
        temp_node_connection = TempCardNodeConnectionFactory(
            total_votes=VOTES_THRESHOLD
        )

        self.assertTrue(temp_node_connection._passes_vote_threshold())

    def test_above_votes_threshold_does_pass_threshold_test(self):
        temp_node_connection = TempCardNodeConnectionFactory(
            total_votes=VOTES_THRESHOLD+1
        )

        self.assertTrue(temp_node_connection._passes_vote_threshold())

    def test_under_percent_votes_threshold_does_not_pass_threshold_test(self):
        temp_node_connection = TempCardNodeConnectionFactory(
            total_votes=100,
            votes_for=int(100*VOTES_THRESHOLD_PERCENT) - 1
        )

        self.assertFalse(temp_node_connection._passes_vote_percent_threshold())

    def test_at_percent_votes_threshold_does_pass_threshold_test(self):
        temp_node_connection = TempCardNodeConnectionFactory(
            total_votes=100,
            votes_for=int(100*VOTES_THRESHOLD_PERCENT)
        )

        self.assertTrue(temp_node_connection._passes_vote_percent_threshold())

    def test_above_percent_votes_threshold_does_pass_threshold_test(self):
        temp_node_connection = TempCardNodeConnectionFactory(
            total_votes=100,
            votes_for=int(100*VOTES_THRESHOLD_PERCENT) + 1
        )

        self.assertTrue(temp_node_connection._passes_vote_percent_threshold())

    def test_add_vote_for_adds_to_votes_for_and_total(self):
        start_votes_for = 0
        start_total_votes = 5

        temp_node_connection = TempCardNodeConnectionFactory(
            total_votes=start_total_votes,
            votes_for=start_votes_for
        )

        temp_node_connection.add_vote_for()

        self.assertEqual(temp_node_connection.total_votes, start_total_votes + 1)
        self.assertEqual(temp_node_connection.votes_for, start_votes_for + 1)

    def test_add_vote_against_adds_to_votes_for_and_total(self):
        start_votes_for = 0
        start_total_votes = 5

        temp_node_connection = TempCardNodeConnectionFactory(
            total_votes=start_total_votes,
            votes_for=start_votes_for
        )

        temp_node_connection.add_vote_against()

        self.assertEqual(temp_node_connection.total_votes, start_total_votes+1)
        self.assertEqual(temp_node_connection.votes_for, start_votes_for)

    def test_at_percent_threshold_and_at_vote_threshold_can_be_made_permanent(self):
        temp_node_connection = TempCardNodeConnectionFactory(
            total_votes=VOTES_THRESHOLD,
            votes_for=int(VOTES_THRESHOLD * VOTES_THRESHOLD_PERCENT) + 1
        )

        self.assertTrue(temp_node_connection.can_make_permanent())

    def test_below_percent_threshold_and_at_vote_threshold_cannot_be_made_permanent(self):
        temp_node_connection = TempCardNodeConnectionFactory(
            total_votes=VOTES_THRESHOLD,
            votes_for=int(VOTES_THRESHOLD * VOTES_THRESHOLD_PERCENT) - 1
        )

        self.assertFalse(temp_node_connection.can_make_permanent())

    def test_at_percent_threshold_and_below_vote_threshold_can_be_made_permanent(self):
        temp_node_connection = TempCardNodeConnectionFactory(
            total_votes=VOTES_THRESHOLD - 1,
            votes_for=int(VOTES_THRESHOLD * VOTES_THRESHOLD_PERCENT) + 1
        )

        self.assertFalse(temp_node_connection.can_make_permanent())

    def test_below_percent_threshold_and_below_vote_threshold_can_be_made_permanent(self):
        temp_node_connection = TempCardNodeConnectionFactory(
            total_votes=VOTES_THRESHOLD - 1,
            votes_for=int(VOTES_THRESHOLD * VOTES_THRESHOLD_PERCENT) - 5
        )

        self.assertFalse(temp_node_connection.can_make_permanent())
