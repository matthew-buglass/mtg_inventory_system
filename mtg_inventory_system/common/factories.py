from datetime import datetime

import factory
import uuid

from common.const import CARD_LAYOUT_OPTIONS
from common.models import Card, CardSet


class CardSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CardSet

    id = factory.LazyAttribute(lambda _: uuid.uuid4())
    name = factory.LazyAttribute(lambda _: factory.Faker('name'))
    symbol = factory.LazyAttribute(lambda _: factory.Faker('random_letter'))
    set_type = factory.LazyAttribute(lambda _: factory.Faker('random_letter'))
    scryfall_uri = factory.LazyAttribute(lambda _: factory.Faker('uri'))
    scryfall_set_cards_uri = factory.LazyAttribute(lambda _: factory.Faker('uri'))
    icon_uri = factory.LazyAttribute(lambda _: factory.Faker('uri'))


class CardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Card

    id = factory.LazyAttribute(lambda _: uuid.uuid4())
    scryfall_uri = factory.LazyAttribute(lambda _: factory.Faker('uri'))
    scryfall_url = factory.LazyAttribute(lambda _: factory.Faker('safe_domain_name'))

    layout = factory.LazyAttribute(lambda _: factory.Faker('random_element', elements=[opt[0] for opt in CARD_LAYOUT_OPTIONS]))
    name = factory.LazyAttribute(lambda _: factory.Faker('name'))

    conv_mana_cost = factory.LazyAttribute(lambda _: factory.Faker('random_digit'))

    released_at = factory.LazyAttribute(lambda _: factory.Faker('date_between'))
    time_added_to_db = factory.LazyAttribute(lambda _: datetime.today())
    last_updated = factory.LazyAttribute(lambda _: datetime.today())

    collector_number = factory.LazyAttribute(lambda _: factory.Faker('random_letter'))

    # Foreign Relations
    card_set = factory.SubFactory(CardSetFactory)
