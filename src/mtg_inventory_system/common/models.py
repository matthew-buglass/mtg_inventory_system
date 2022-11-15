import datetime
import re
import uuid
import logging

from django.core.exceptions import FieldError
from django.db import models
from django.db.models import Count, F

from .const import CARD_LAYOUT_OPTIONS, PRINTING_TYPE_OPTIONS

logger = logging.getLogger(__name__)


#####    Non-card related   #####
class User(models.Model):
    """Represents a user of the system
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)

    # TODO: Replace with google OAuth
    username = models.CharField(max_length=64)

    def get_card_library_query_set(self):
        return Card.objects.filter(cardownership__user__id=self.id)

    def get_unique_card_library_query_set(self):
        return self.get_card_library_query_set().distinct()

    def get_unique_card_library_count_query_set(self):
        return self.get_card_library_query_set().annotate(count=Count('unique_string'))


#########      Storage    ##########
class StorageLocation(models.Model):
    """Model for tracking where cards are stored
    """
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)


##########      Cards     ############
class CardSet(models.Model):
    """The set that a card is a part of
    """
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=500)
    symbol = models.CharField(max_length=8)
    set_type = models.CharField(max_length=20)
    scryfall_uri = models.URLField()
    scryfall_set_cards_uri = models.URLField()
    icon_uri = models.URLField(null=True)


class ManaCost(models.Model):
    green = models.PositiveSmallIntegerField(null=True, default=None)
    red = models.PositiveSmallIntegerField(null=True, default=None)
    blue = models.PositiveSmallIntegerField(null=True, default=None)
    black = models.PositiveSmallIntegerField(null=True, default=None)
    white = models.PositiveSmallIntegerField(null=True, default=None)
    colourless = models.PositiveSmallIntegerField(null=True, default=None)
    x_mana = models.BooleanField(default=False)
    other = models.BooleanField(default=False)

    class Meta:
        unique_together = ('green', 'red', 'blue', 'black', 'white', 'colourless')

    @staticmethod
    def _parse_scryfall_json_to_model_args(mana_json_string):
        mana = {}

        mana_regex = r'\{[1-9A-Z]\}'
        alt_mana_regex = r'\{B/P\}'
        mana_breakdown = re.findall(mana_regex, mana_json_string)
        alt_mana_breakdown = re.findall(alt_mana_regex, mana_json_string)

        for mana_sym in mana_breakdown:
            symbol = mana_sym.replace('{', "").replace("}", "")
            try:
                un_col = int(symbol)
                mana['un_col'] = un_col
            except ValueError:
                num = mana.get(symbol) or 0
                mana[symbol] = num + 1

        return {
            'green': mana.get('G'),
            'red': mana.get('R'),
            'blue': mana.get('U'),
            'black': mana.get('B'),
            'white': mana.get('W'),
            'colourless': mana.get('un_col'),
            'x_mana': mana.get('x') is not None,
            'other': len(alt_mana_breakdown) > 0,
        }

    @classmethod
    def get_or_create_from_scryfall_json(cls, mana_json_string):
        args_dict = cls._parse_scryfall_json_to_model_args(mana_json_string)
        return cls.objects.get_or_create(**args_dict)

    @classmethod
    def update_or_create_from_scryfall_json(cls, mana_json_string):
        args_dict = cls._parse_scryfall_json_to_model_args(mana_json_string)
        return cls.objects.update_or_create(**args_dict)


class CardFace(models.Model):
    """Sometimes MTG cards can have more than one face tied to it. This represents that data
    """
    name = models.CharField(max_length=128)
    mana_cost = models.ForeignKey(ManaCost, on_delete=models.DO_NOTHING, null=True, default=None)

    power = models.SmallIntegerField(null=True)
    toughness = models.SmallIntegerField(null=True)

    type_line = models.CharField(max_length=100)
    oracle_text = models.CharField(max_length=500)
    small_img_uri = models.URLField(null=True)
    normal_img_uri = models.URLField(null=True)

    @staticmethod
    def _parse_scryfall_json_to_model_args(card_face_json):
        try:
            toughness = int(card_face_json.get('toughness'))
        except ValueError:
            toughness = -1

        try:
            power = int(card_face_json.get('power'))
        except ValueError:
            power = -1

        return {
            'name': card_face_json['name'],
            'mana_cost': ManaCost.get_or_create_from_scryfall_json(card_face_json['mana_cost'])[0],
            'power': power,
            'toughness': toughness,
            'type_line': card_face_json['type_line'],
            'oracle_text': card_face_json['oracle_text'],
            'small_img_uri': card_face_json.get('image_uris').get('small'),
            'normal_img_uri': card_face_json.get('image_uris').get('normal'),
        }

    @classmethod
    def get_or_create_from_scryfall_json(cls, card_face_json):
        args_dict = cls._parse_scryfall_json_to_model_args(card_face_json)
        return cls.objects.get_or_create(**args_dict)

    @classmethod
    def update_or_create_from_scryfall_json(cls, card_face_json):
        args_dict = cls._parse_scryfall_json_to_model_args(card_face_json)
        return cls.objects.update_or_create(**args_dict)


class Card(models.Model):
    """Represents a unique card in Magic's printing
    """
    id = models.UUIDField(primary_key=True)
    scryfall_uri = models.URLField()
    scryfall_url = models.URLField()

    layout = models.CharField(max_length=20, choices=CARD_LAYOUT_OPTIONS)
    name = models.CharField(max_length=500)

    conv_mana_cost = models.PositiveSmallIntegerField()
    printing_type = models.CharField(max_length=10, choices=PRINTING_TYPE_OPTIONS, default='normal')

    released_at = models.DateField(default=datetime.date(year=1993, month=9, day=1))
    time_added_to_db = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # Foreign Relations
    face_primary = models.ForeignKey(CardFace, on_delete=models.CASCADE, related_name='face_primary')
    face_secondary = models.ForeignKey(CardFace, on_delete=models.CASCADE, null=True, related_name='face_secondary')
    card_set = models.ForeignKey(CardSet, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = ('id', 'printing_type')

    def __str__(self):
        return f'{self.name} - {self.printing_type} - {self.card_set.name}'

    @property
    def unique_string(self):
        return "{} {}".format(self.id, self.printing_type)
    
    @staticmethod
    def _parse_scryfall_json_to_model_args(card_json):
        card_faces = card_json.get('card_faces')

        if card_faces and len(card_faces) == 2:
            if not card_faces[0].get('image_uris'):
                card_faces[0]['image_uris'] = card_json['image_uris']
                card_faces[1]['image_uris'] = card_json['image_uris']

            primary_face_json = CardFace._parse_scryfall_json_to_model_args(card_faces[0])
            secondary_face_json = CardFace._parse_scryfall_json_to_model_args(card_faces[1])

            primary_face = CardFace.objects.get_or_create(
                name=primary_face_json['name'],
                mana_cost=primary_face_json['mana_cost'],
                power=primary_face_json['power'],
                toughness=primary_face_json['toughness'],
                type_line=primary_face_json['type_line'],
                oracle_text=primary_face_json['oracle_text'],
                small_img_uri=primary_face_json['small_img_uri'],
                normal_img_uri=primary_face_json['normal_img_uri'],
            )[0]
            secondary_face = CardFace.objects.get_or_create(
                name=secondary_face_json['name'],
                mana_cost=secondary_face_json['mana_cost'],
                power=secondary_face_json['power'],
                toughness=secondary_face_json['toughness'],
                type_line=secondary_face_json['type_line'],
                oracle_text=secondary_face_json['oracle_text'],
                small_img_uri=secondary_face_json['small_img_uri'],
                normal_img_uri=secondary_face_json['normal_img_uri'],
            )[0]
        elif card_faces and len(card_faces) > 2:
            error_msg = "Cannot create a card {} with {} faces / alternates. url: {}".format(card_json['name'],
                                                                                             len(card_faces),
                                                                                             card_json['url'])
            logger.error(error_msg)
            raise FieldError(error_msg)
        else:
            mana_cost = ManaCost.get_or_create_from_scryfall_json(card_json['mana_cost'])[0]
            try:
                toughness = int(card_json.get('toughness'))
            except ValueError:
                toughness = -1

            try:
                power = int(card_json.get('power'))
            except ValueError:
                power = -1

            primary_face = CardFace.objects.get_or_create(
                name=card_json['name'],
                mana_cost=mana_cost,
                power=power,
                toughness=toughness,
                type_line=card_json['type_line'],
                oracle_text=card_json['oracle_text'],
                small_img_uri=card_json['image_uris']['small'],
                normal_img_uri=card_json['image_uris']['normal'],
            )[0]
            secondary_face = None

        card_set = CardSet.objects.get_or_create(
            id=card_json['set_id'],
            name=card_json['set_name'],
            symbol=card_json['set'],
            scryfall_uri=card_json['set_uri'],
            scryfall_set_cards_uri=card_json['set_search_uri'],
        )[0]

        return {
            'id': card_json['id'],
            'scryfall_uri': card_json['uri'],
            'scryfall_url': card_json['scryfall_uri'],
            'layout': card_json['layout'],
            'name': card_json['name'],
            'released_at': card_json['released_at'],
            'conv_mana_cost': int(card_json['cmc']),
            'face_primary': primary_face,
            'face_secondary': secondary_face,
            'card_set': card_set,
        }

    @staticmethod
    def get_raw_json_for_bulk_operations(card_json):
        json_with_objs = Card._parse_scryfall_json_to_model_args(card_json)
        json_to_return = {}

        for key, value in json_with_objs.items():
            if isinstance(value, models.Model):
                new_key = "{}__id".format(key)
                json_to_return[new_key] = value.pk
            else:
                json_to_return[key] = value

        return json_to_return

    @classmethod
    def get_or_create_from_scryfall_json(cls, card_json):
        args_dict = cls._parse_scryfall_json_to_model_args(card_json)
        return cls.objects.get_or_create(**args_dict)

    @classmethod
    def update_or_create_from_scryfall_json(cls, card_json):
        args_dict = cls._parse_scryfall_json_to_model_args(card_json)
        return cls.objects.update_or_create(**args_dict)


class CardOwnership(models.Model):
    """Represents and instance of a card in a user's library. So a user can have multiple copies of the same card
    """
    # Foreign Relations
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    card = models.ForeignKey(Card, on_delete=models.DO_NOTHING)
    date_added = models.DateField(auto_now_add=True)
    date_removed = models.DateField(null=True)
    price_purchased = models.DecimalField(decimal_places=2, max_digits=9)
    price_sold = models.DecimalField(decimal_places=2, max_digits=9, null=True)


class CardPrice(models.Model):
    """Tracks how much a card cost in USD on a certain day
    """
    date = models.DateField(auto_now_add=True)
    price_usd = models.DecimalField(decimal_places=2, max_digits=9)
    price_tix = models.DecimalField(decimal_places=2, max_digits=9)
    prince_eur = models.DecimalField(decimal_places=2, max_digits=9)
    card = models.ForeignKey(Card, on_delete=models.DO_NOTHING)


########      Decks     ############
class Deck(models.Model):
    """Represents a constructed Deck
    """
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    cards = models.ManyToManyField(Card)
    current_location = models.ForeignKey(StorageLocation, on_delete=models.DO_NOTHING, null=True)

    def is_valid(self):
        raise NotImplemented


class ConstructedDeck(Deck):
    """Represents a deck for a 60 card constructed format
    """
    format_name = models.CharField(max_length=15, choices=[
        ('Standard', 'standard'),
        ('Modern', 'modern'),
        ('Pioneer', 'pioneer'),
        ('Historic', 'historic'),
        ('Legacy', 'legacy'),
        ('Vintage', 'vintage'),
        ('Pauper', 'pauper'),
    ])
    sideboard = models.ManyToManyField(Card)


class CommanderDeck(Deck):
    """Represents a deck for the commander format
    """
    commander = models.ForeignKey(Card, on_delete=models.DO_NOTHING, related_name='commander')
    secondary_commander = models.ForeignKey(Card, on_delete=models.DO_NOTHING, null=True,
                                            related_name='secondary_commander')
