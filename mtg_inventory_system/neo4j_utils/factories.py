import random
from datetime import datetime

import factory
import uuid

from faker import Factory

from common.factories import CardFactory
from neo4j_utils.models import CardNodeConnection, TempCardNodeConnection

faker = Factory.create('en_CA')


class CardNodeConnectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CardNodeConnection

    src_card = factory.SubFactory(CardFactory)
    dst_card = factory.SubFactory(CardFactory)
    connection_type = 'triggers'
    connection_meta_data = {}


class TempCardNodeConnectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TempCardNodeConnection

    src_card = factory.SubFactory(CardFactory)
    dst_card = factory.SubFactory(CardFactory)
    connection_type = 'triggers'
    connection_meta_data = {}
    votes_for = random.randint(0, 7)
    total_votes = factory.LazyAttribute(lambda self: self.votes_for + random.randint(0, 7))
