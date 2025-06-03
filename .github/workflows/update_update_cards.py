import bs4
import requests
import subprocess
from pathlib import Path

from hearthstone import cardxml

from update_cards import CARD_SETS, LATEST_CARD_SET

def download_set_image(card_set_id):
  repo_root = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip())

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
  contents = contents[:end_line] + new_set_line + contents[end_line:]
  
  for i in range(len(contents)):
    if contents[i].startswith('  STANDARD_RANGE ='):
      contents[i] = new_standard_range

  with update_cards.open('w') as f:
    f.write('\n'.join(contents))

"""

  raise ValueError("Could not find set icon for core set, please rename the image when adjusting the standard range")
    raise ValueError(f'Found card data from an unknown set: {card.card_set.name}. Was there an expansion recently? If so, please update the CARD_SETS and STANDARD_RANGE variables.')

def 
"""

if __name__ == '__main__':
  cardid_db, _ = cardxml.load()
  latest_card_sets = set()
  for card in cardid_db.values():
    if card.card_set.name not in CARD_SETS:
      latest_card_sets.add(card.card_set.name)
  print(f'Latest card sets: {latest_card_sets}')
  if len(latest_card_sets) != 1:
    raise ValueError('Could not determine card sets')

  for card_set in latest_card_sets:
    card_set_id = LATEST_CARD_SET + 1
    card_set_title = download_set_image(card_set_id)

    # TODO: Rotation is a ??? for later, but the required actions are:
    # - update the min value for STANDARD_RANGE
    # - compute CORE_SET = STANDARD_RANGE[0] - 0.5
    # - rename the core_set image

    new_set_line = f"  '{card_set}': {card_set_id:0.1f}, # {card_set_title}"
    new_standard_line = f"  STANDARD_RANGE = [32.0, {card_set_id:0.1f}] # Inclusive on both ends"
    add_card_set(new_set_line, new_standard_line)
    
