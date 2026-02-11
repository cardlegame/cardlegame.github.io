import bs4
import requests
import subprocess
from pathlib import Path
from datetime import datetime

from hearthstone import cardxml
from hearthstone.enums import CardType, CardSet

from update_cards import CARD_SETS, LATEST_CARD_SET, STANDARD_RANGE

repo_root = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip())

def download_set_image(card_set_id):
  r = requests.get('https://hearthstone.blizzard.com/en-us/expansions-adventures')
  r.raise_for_status()
  soup = bs4.BeautifulSoup(r.text, 'html.parser')
  expansion_imgs = soup.find_all('img', {'class': 'CardSetLogo'})
  for i, img in enumerate(expansion_imgs[:3]):
    r = requests.get(img['src'])

    already_downloaded = False
    for file in Path(f'{repo_root}/public/sets/').glob('*.png'):
      with file.open('rb') as f:
        new_contents = f.read()
        if new_contents == r.content:
          break
    else:
      print(f'Found unique image for new set "{img["alt"]}", saving as latest set')
      with Path(f'{repo_root}/public/sets/{card_set_id:.0f}.png').open('wb') as f:
        f.write(r.content)
      return img['alt'] # Latest set name
  else:
    raise ValueError('Failed to automatically download the expansion image')

def add_card_set(new_set_line, new_standard_range):
  update_cards = Path(__file__).with_name('update_cards.py')
  with update_cards.open('r') as f:
    contents = f.read().split('\n')

  end_line = contents.index('} # end CARD_SETS')
  contents = contents[:end_line] + [new_set_line] + contents[end_line:]

  for i in range(len(contents)):
    if 'STANDARD_RANGE =' in contents[i]:
      contents[i] = new_standard_range

  with update_cards.open('w') as f:
    f.write('\n'.join(contents))

def add_garbage_set(new_set_line):
  update_cards = Path(__file__).with_name('update_cards.py')
  with update_cards.open('r') as f:
    contents = f.read().split('\n')

  in_card_sets = False
  for i, line in enumerate(contents):
    if 'CARD_SETS = {' in line:
      in_card_sets = True
    elif '} # end CARD_SETS' in line:
      in_card_sets = False
    elif in_card_sets and 'None' not in line and 'None' in contents[i-1]:
      contents.insert(i, new_set_line)
      break

  with update_cards.open('w') as f:
    f.write('\n'.join(contents))

def add_new_year(new_year):
  update_cards = Path(__file__).with_name('update_cards.py')
  with update_cards.open('r') as f:
    contents = f.read().split('\n')

  end_sets = contents.index('} # end CARD_SETS')
  for line in contents[end_sets:0:-1]:
    if line.startswith('  # ') and line[4:].isdigit():
      latest_year = int(line[4:])
      break

  if new_year == latest_year:
    return False

  contents.insert(end_sets, '')
  contents.insert(end_sets, f'  # {new_year}')

  with update_cards.open('w') as f:
    f.write('\n'.join(contents))
  return True

if __name__ == '__main__':
  cardid_db, _ = cardxml.load()
  latest_card_sets = set()
  garbage_card_sets = set()
  for card in cardid_db.values():
    if card.card_set.name in CARD_SETS:
      pass # Already parsed
    elif card.type != CardType.MINION or card.collectible != True:
      garbage_card_sets.add(card.card_set.name)
    else:
      latest_card_sets.add(card.card_set.name)
  garbage_card_sets -= latest_card_sets # If any card was not garbage, the set is not garbage
  print(f'Latest card sets: {latest_card_sets}')
  print(f'Garbage card sets: {garbage_card_sets}')
  if len(latest_card_sets) != 1:
    raise ValueError('Could not determine card sets')

  for card_set in garbage_card_sets:
    new_set_line = f"  '{card_set}': None,"
    add_garbage_set(new_set_line)

  if add_new_year(datetime.now().year):
    print('NEW YEAR, NEW CARDS, NEW STANDARD_RANGE')
    old_core_set = STANDARD_RANGE[0] - 0.5
    STANDARD_RANGE[0] += 3.0
    new_core_set = STANDARD_RANGE[0] - 0.5
    Path(f'{repo_root}/public/sets/{old_core_set:.1f}.png').rename(f'{repo_root}/public/sets/{new_core_set:.1f}.png')

  for card_set in latest_card_sets:
    card_set_id = LATEST_CARD_SET + 1
    card_set_title = download_set_image(card_set_id)

    new_set_line = f"  '{card_set}': {card_set_id:0.1f}, # {card_set_title}"
    new_standard_line = f'STANDARD_RANGE = [{STANDARD_RANGE[0]}, {card_set_id:0.1f}] # Inclusive on both ends'
    add_card_set(new_set_line, new_standard_line)
