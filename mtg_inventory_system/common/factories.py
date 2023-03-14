import random
from datetime import datetime

import factory
import uuid

from common.const import CARD_LAYOUT_OPTIONS
from common.models import Card, CardSet
from faker import Factory

faker = Factory.create('en_CA')

class CardSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CardSet

    id = factory.LazyAttribute(lambda _: uuid.uuid4())
    name = factory.LazyAttribute(lambda _: factory.Faker('name'))
    symbol = 'abc'
    set_type = 'regular'
    scryfall_uri = factory.LazyAttribute(lambda _: factory.Faker('uri'))
    scryfall_set_cards_uri = factory.LazyAttribute(lambda _: factory.Faker('uri'))
    icon_uri = factory.LazyAttribute(lambda _: factory.Faker('uri'))


class CardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Card

    id = factory.LazyAttribute(lambda _: uuid.uuid4())
    scryfall_uri = factory.LazyAttribute(lambda _: factory.Faker('uri'))
    scryfall_url = factory.LazyAttribute(lambda _: factory.Faker('safe_domain_name'))

    layout = 'regular'
    name = factory.LazyAttribute(lambda _: faker.name())

    conv_mana_cost = factory.LazyAttribute(lambda _: random.randint(0, 7))

    released_at = factory.LazyAttribute(lambda _: faker.past_date())
    time_added_to_db = factory.LazyAttribute(lambda _: datetime.today())
    last_updated = factory.LazyAttribute(lambda _: datetime.today())

    collector_number = 'abc123'

    # Foreign Relations
    card_set = factory.SubFactory(CardSetFactory)
