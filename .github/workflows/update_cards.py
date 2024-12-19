import copy
import json
import subprocess
from pathlib import Path

from hearthstone import cardxml
from hearthstone.enums import CardType, CardSet

CLASS_NAMES = {
  'DEMONHUNTER': 'DemonHunter',
  'MAGE': 'Mage',
  'DRUID': 'Druid',
  'SHAMAN': 'Shaman',
  'HUNTER': 'Hunter',
  'PRIEST': 'Priest',
  'NEUTRAL': 'Neutral',
  'WARLOCK': 'Warlock',
  'ROGUE': 'Rogue',
  'WARRIOR': 'Warrior',
  'PALADIN': 'Paladin',
  'DEATHKNIGHT': 'DeathKnight',
}

RARITIES = {
  'FREE': 0,
  'COMMON': 1,
  'RARE': 2,
  'EPIC': 3,
  'LEGENDARY': 4,
}

CARD_SETS = {
  # Filtered out
  'INVALID': None,
  'TB': None, # Tavern Brawl
  'BATTLEGROUNDS': None,
  'LETTUCE': None, # Mercenaries
  'PLACEHOLDER_202204': None,
  'EVENT': None,

  # Valid, but lower priority than actual sets
  'CORE': -2.0,
  'VANILLA': -1.0,
  'LEGACY': 0.0,
  'EXPERT1': 0.0,

  # 2015
  'NAXX': 1.0, # Curse of Naxxramas
  'GVG': 2.0, # Goblins vs Gnomes
  'BRM': 3.0, # Blackrock Mountain
  'TGT': 4.0, # The Grand Tournament
  'LOE': 5.0, # The League of Explorers

  # 2016
  'OG': 6.0, # Whispers of the Old Gods
  'KARA': 7.0, # One Night in Karazhan
  'GANGS': 8.0, # Mean Streets of Gadgetzan

  # 2017
  'UNGORO': 9.0, # Journey to Un'Goro
  'ICECROWN': 10.0, # Knights of the Frozen Throne
  'LOOTAPALOOZA': 11.0, # Kobolds & Catacombs

  # 2018
  'GILNEAS': 12.0, # The Witchwood
  'BOOMSDAY': 13.0, # The Boomsday Project
  'TROLL': 14.0, # Rastakhan's Rumble

  # 2019
  'DALARAN': 15.0, # Rise of Shadows
  'ULDUM': 16.0, # Saviours of Uldum
  'DRAGONS': 17.0, # Descent of Dragons
  'YEAR_OF_THE_DRAGON': 17.0, # ??? Maybe Galakrond's Awakening?

  # 2020
  'BLACK_TEMPLE': 19.0, # Ashes of Outlands
  'DEMON_HUNTER_INITIATE': 19.5,
  'SCHOLOMANCE': 20.0, # Scholomance Academy
  'DARKMOON_FAIRE': 21.0, # Madness at the Darkmoon Faire

  # 2021
  'THE_BARRENS': 22.0, # Forged in the Barrens
  'STORMWIND': 23.0, # United in Stormwind
  'ALTERAC_VALLEY': 24.0, # Fractured in Alterac Valley

  # 2022
  'THE_SUNKEN_CITY': 25.0, # Voyage to the Sunken City
  'REVENDRETH': 26.0, # Murder at Castle Nathria
  'PATH_OF_ARTHAS': 26.5, # ???
  'RETURN_OF_THE_LICH_KING': 27.0, # Return of the Lich King

  # 2023
  'BATTLE_OF_THE_BANDS': 28.0, # Festival of Legends
  'TITANS': 29.0, # Titans
  'WILD_WEST': 30.0, # Showdown in the Badlands

  # 2024
  'WONDERS': 31.0, # Caverns of Time
  'WHIZBANGS_WORKSHOP': 32.0, # Whizbang's Workshop
  'ISLAND_VACATION': 33.0, # Perils in Paradise
  'SPACE': 34.0, # Great Dark Beyond
}

converted_cards = {}

# Import all cards from hearthsim data
cardid_db, _ = cardxml.load()
for card in cardid_db.values():
  if card.type != CardType.MINION or card.collectible != True:
    continue # Cardle only supports collectible minions

  if card.card_set.name not in CARD_SETS:
    raise ValueError(f'Found card data from an unknown set: {card.card_set.name}. Was there an expansion recently? If so, please update the CARD_SETS and STANDARD_RANGE variables.')

  card_set = CARD_SETS[card.card_set.name]
  if card_set is None:
    continue # Ignore garbage data

  # Some cards were reprinted in later sets, possibly with different stats. Keep all (valid) copies of the card for future filtering.
  if card.name not in converted_cards:
    converted_cards[card.name] = []
  converted_cards[card.name].append({
    'cardClass': CLASS_NAMES[card.card_class.name],
    'cost': float(card.cost),
    'name': card.name,
    'rarity': RARITIES[card.rarity.name],
    'set': card_set,
    'attack': float(card.atk),
    'health': float(card.health),
  })

# Filter cards into the various sets
wild_cards = []
wild_legendaries = []
classic_cards = []
standard_cards = []

STANDARD_RANGE = [28.0, 34.0] # Inclusive on both ends

alphabetized_names = sorted(converted_cards.keys())

for card_name in alphabetized_names:
  cards = converted_cards[card_name]

  # For wild datasets, use the copy of the card from the most recent set
  card = max(cards, key=lambda card: card['set'])
  if card['set'] == -2.0:
    card['set'] = 24.5 # Fixup for 'Core', which is identified as 24.5 but has lowest priority.

  # Any card from any non-classic set
  if card['set'] >= 0:
    wild_cards.append(card)

  # Legendary card from any non-classic set
  if card['rarity'] == 4 and card['set'] >= 0:
    wild_legendaries.append(card)

  # If any variant is from the classic set, use that.
  classic_card = next((card for card in cards if card['set'] == -1.0), None)
  if classic_card:
    classic_card = copy.copy(classic_card)
    classic_card['set'] = -1
    classic_cards.append(classic_card)

  for card in cards:
    if card['set'] == 31.0:
      continue # Caverns of Time was a direct-to-wild set.
    if card['set'] == -2.0:
      card['set'] = 24.5 # This is our name for the core set. Deal with it, I guess.
    if card['set'] == 24.5 or (STANDARD_RANGE[0] <= card['set'] <= STANDARD_RANGE[1]):
      standard_cards.append(card)
      break

repo_root = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip())
data_folder = repo_root / 'src' / 'data'

def compare_and_write(file, new_contents):
  with file.open('r') as f:
    old_contents = json.load(f)

  new_cards_dict = {card['name']:card for card in new_contents}
  for old_card in old_contents:
    card_name = old_card['name']
    new_card = new_cards_dict.get(card_name, None)
    if not new_card:
      print(f'Card {card_name} was removed from {file.name}')
      print('Old:', old_card)
      continue
    if old_card != new_card:
      print(f'Card {card_name} was changed in {file.name}')
      print('Old:', old_card)
      print('New:', new_card)
    del new_cards_dict[card_name]

  for card_name, new_card in new_cards_dict:
    print(f'Card {card_name} was added to {file.name}')
    print('new:', new_card)

  with file.open('w') as f:
    json.dump(new_contents, f)

compare_and_write(data_folder / 'wild.json', wild_cards)
compare_and_write(data_folder / 'wildlegendaries.json', wild_legendaries)
compare_and_write(data_folder / 'classic.json', classic_cards)
compare_and_write(data_folder / 'standard.json', standard_cards)