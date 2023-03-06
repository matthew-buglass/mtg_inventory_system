# Constraints
CREATE CONSTRAINT unique_card_name [IF NOT EXISTS] FOR (card:Card) REQUIRE n.name IS UNIQUE;