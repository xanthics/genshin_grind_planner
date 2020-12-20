from browser import document as doc
from browser import bind
from browser.html import TABLE, TR, TH, TD, INPUT, SELECT, OPTION, DIV, BUTTON, SPAN, LI, H2, H3, IMG, COLGROUP, COL, SECTION
from browser.local_storage import storage

from characters import characters
from weapons import weapons
from artifacts import artifacts
from lang_en import strings
from costs import costs
from farming_data import farming_data
from traveler import traveler
from ingame_order import ingame_order


storage_key = "genshin_grind_planner"
current_page = 'character'  # are we on character or inventory page
# dict to store states for the grind table
grind_table_state = {
	'checked': set(),  # is a character selected
	'characters': {},  # row state for every possible character
	'arti_check': set(),  # is a character's artifacts selected
	'artifacts': set(),  # ids of all currently selected artifacts
	'user': {},  # the amount of each item the user has
	'total': {}  # the amount of each item needed, to detect changes
}
# to hold the initial stat of 'characters' for when we initialize or reset data
char_dict = {}


# Setter storage so that we can differentiate values on this site from others at the same domain
def set_storage(key, val):
	storage[f"{storage_key}-{key}"] = val


# Getter for storage so that we can differentiate values on this site from others at the same domain
def get_storage(key):
	return storage[f"{storage_key}-{key}"]


# deleter for storage so that we can differentiate values on this site from others at the same domain
def del_storage(key):
	nkey = f"{storage_key}-{key}"
	if nkey in storage.keys():
		del storage[nkey]


# Check if a value exists in storage
def check_storage(key):
	return f"{storage_key}-{key}" in storage


# Reset that only deletes values for this site
def reset_data(ev):
	grind_table_state['checked'] = set()
	for char in grind_table_state['characters']:
		grind_table_state['characters'][char] = char_dict.copy()
		grind_table_state['arti_check'].add(char)
	grind_table_state['artifacts'] = set()
	for val in grind_table_state['user']:
		grind_table_state['user'][val] = 0
		grind_table_state['total'][val] = 0
	for elt in doc.get(selector='input[type=checkbox]'):
		if 'char_select' in elt.attrs['class']:
			doc[elt.id].checked = False
		else:
			doc[elt.id].checked = True
	for elt in doc.get(selector='select'):
		elt.selectedIndex = 0
	for elt in doc.get(selector='TR[data-id]'):
		elt.attrs['class'] = 'unchecked'
	for elt in doc.get(selector='.saved_arti'):
		del doc[elt.id]
	for elt in doc.get(selector='input[type=number]'):
		elt.value = 0

	for key in storage.keys():
		if key.startswith(storage_key):
			del storage[key]
	calculate_change()


# Reset that only deletes values for this site
def reset_character(ev):
	grind_table_state['checked'] = set()
	for char in grind_table_state['characters']:
		grind_table_state['characters'][char] = char_dict.copy()
		grind_table_state['arti_check'].add(char)
	grind_table_state['artifacts'] = set()
	for val in grind_table_state['total']:
		grind_table_state['total'][val] = 0
	for elt in doc.get(selector='input[type=checkbox]'):
		if 'char_select' in elt.attrs['class']:
			doc[elt.id].checked = False
		else:
			doc[elt.id].checked = True
	for elt in doc.get(selector='select'):
		elt.selectedIndex = 0
	for elt in doc.get(selector='TR[data-id]'):
		elt.attrs['class'] = 'unchecked'
	for elt in doc.get(selector='.saved_arti'):
		del doc[elt.id]

	for key in storage.keys():
		if key.startswith(storage_key) and not key.endswith('-user'):
			del storage[key]
	calculate_change()


# Reset that only deletes values for this site
def reset_inventory(ev):
	for val in grind_table_state['user']:
		grind_table_state['user'][val] = 0
	for elt in doc.get(selector='input[type=number]'):
		elt.value = 0

	for key in storage.keys():
		if key.startswith(storage_key) and key.endswith('-user'):
			del storage[key]
	calculate_change()


# generator to get all values in storage.  used during page load to set things up
def list_storage():
	for val in storage:
		if val.startswith(storage_key):
			yield val[len(storage_key) + 1:], storage[val]


# initialize the global variable state and restore page state from local storage
def init_page():
	global char_dict
	char_keys = []
	for elt in doc.get(selector=f".amber"):
		char_keys.append((elt.id.split('-')[0], elt.value))
	char_dict = {k: int(v) if v.isnumeric() else v for k, v in char_keys}

	for elt in doc.get(selector='.char_select'):
		name = elt.id.split('-')[1]
		grind_table_state['characters'][name] = char_dict.copy()
		grind_table_state['arti_check'].add(name)

	# for tracking state without querying the DOM constantly
	grind_table_state['user'][f"xp"] = 0
	grind_table_state['user'][f"xp_sub_1"] = 0
	grind_table_state['user'][f"xp_sub_0"] = 0
	grind_table_state['user'][f"wep_xp"] = 0
	grind_table_state['user'][f"wep_xp_sub_1"] = 0
	grind_table_state['user'][f"wep_xp_sub_0"] = 0
	grind_table_state['user'][f"mora"] = 0
	grind_table_state['total'][f"xp"] = 0
	grind_table_state['total'][f"wep_xp"] = 0
	grind_table_state['total'][f"mora"] = 0
	for item in doc.get(selector=f'input[type=number].save'):
		item = item.id.split('-')[0]
		grind_table_state['user'][item] = 0
		grind_table_state['total'][item] = 0

	# load any saved values
	for k, v in list_storage():
		if v == 'checked' and 'check' in k:
			sub_key, char = k.split('-')
			grind_table_state['checked'].add(char)
			doc[k].checked = True
			for elt in doc.get(selector=f'TR[data-id="{k}"]'):
				elt.attrs['class'] = 'checked'
		elif v == 'unchecked':
			sub_key, char = k.split('-')
			grind_table_state['arti_check'].discard(char)
			doc[k].checked = False
		elif 'select' in v:
			sub_key, char = k.split('-')
			val = v.split('-')[1]
			doc[k].value = val
			grind_table_state['characters'][char][sub_key] = int(val) if val.isnumeric() else val
		elif v == 'y':
			target, ev_id = k.rsplit('-', maxsplit=1)
			b = BUTTON(strings[ev_id], Class=f'text_button saved_arti {target.split("-")[1]}', Id=f"{target}-{ev_id}", data_arti=ev_id)
			b.bind('click', delete_me)
			doc[target] <= b
			grind_table_state['artifacts'].add(f"{target}-{ev_id}")
		elif '-user' in k:
			grind_table_state['user'][k.split('-')[0]] = int(v)
			doc[k].value = v
		else:
			print(f"Invalid stored data: {k}, {v}")
	# finish updating page state after loading data
	calculate_change()


# custom implementation of default dict for int
def add_value_int(i_dict, key, val):
	if key not in i_dict:
		i_dict[key] = val
	else:
		i_dict[key] += val


# custom implementation of default dict for int
def add_value_set(i_dict, key, val):
	if key not in i_dict:
		i_dict[key] = {val, }
	else:
		i_dict[key].add(val)


# Function for calculating a specific character's "cost"
# This function also updates table select box classes
def update_per_character(char, char_tracker):
	character = grind_table_state['characters'][char]
	if 'traveler' not in char or char == 'traveler':
		update_xp(char, character, char_tracker)
		update_weapon(char, character, char_tracker)
	if char != 'traveler':
		update_talent(char, character, char_tracker)


# Update grind table calculations for leveling a character
def update_xp(char, character, char_tracker):
	level_c, level_c_flag = character['level_c'] % 10, character['level_c'] // 10
	level_t, level_t_flag = character['level_t'] % 10, character['level_t'] // 10
	if level_t > level_c or (level_t == level_c and level_t_flag > level_c_flag):
		if 'selected' not in doc[f'level_c-{char}'].attrs['class']:
			doc[f'level_c-{char}'].attrs['class'] += ' selected'
			doc[f'level_t-{char}'].attrs['class'] += ' selected'
		if level_c_flag:
			temp = costs['character'][level_c+1]
			grind_table_state['total']['xp'] += temp['xp']
			if temp['xp']:
				add_value_set(char_tracker, 'xp', char)
		if level_t_flag:
			temp = costs['character'][level_t+1]
			grind_table_state['total']['mora'] += temp['mora']
			grind_table_state['total'][f"{characters[char]['ascension']['element_1']}_{temp['element_1'][1]}"] += temp['element_1'][0]
			grind_table_state['total'][characters[char]['ascension']['local']] += temp['local']
			grind_table_state['total'][f"{characters[char]['ascension']['common']}_{temp['common'][1]}"] += temp['common'][0]
			if char != 'traveler':
				grind_table_state['total'][characters[char]['ascension']['element_2']] += temp['element_2']
				if temp['element_2']:
					add_value_set(char_tracker, characters[char]['ascension']['element_2'], char)
			if temp['mora']:
				add_value_set(char_tracker, 'mora', char)
			if temp['element_1'][0]:
				add_value_set(char_tracker, characters[char]['ascension']['element_1'], char)
			if temp['local']:
				add_value_set(char_tracker, characters[char]['ascension']['local'], char)
			if temp['common'][0]:
				add_value_set(char_tracker, characters[char]['ascension']['common'], char)
		for i in range(level_c+1+level_c_flag, level_t+1):
			temp = costs['character'][i]
			grind_table_state['total']['xp'] += temp['xp']
			grind_table_state['total']['mora'] += temp['mora']
			grind_table_state['total'][f"{characters[char]['ascension']['element_1']}_{temp['element_1'][1]}"] += temp['element_1'][0]
			grind_table_state['total'][characters[char]['ascension']['element_2']] += temp['element_2']
			grind_table_state['total'][characters[char]['ascension']['local']] += temp['local']
			grind_table_state['total'][f"{characters[char]['ascension']['common']}_{temp['common'][1]}"] += temp['common'][0]
			if temp['xp']:
				add_value_set(char_tracker, 'xp', char)
			if temp['mora']:
				add_value_set(char_tracker, 'mora', char)
			if temp['element_1'][0]:
				add_value_set(char_tracker, characters[char]['ascension']['element_1'], char)
			if temp['element_2']:
				add_value_set(char_tracker, characters[char]['ascension']['element_2'], char)
			if temp['local']:
				add_value_set(char_tracker, characters[char]['ascension']['local'], char)
			if temp['common'][0]:
				add_value_set(char_tracker, characters[char]['ascension']['common'], char)
	elif 'selected' in doc[f'level_c-{char}'].attrs['class']:
		cl = doc[f'level_c-{char}'].attrs['class'].split()
		del cl[cl.index('selected')]
		clt = ' '.join(cl)
		doc[f'level_c-{char}'].attrs['class'] = clt
		doc[f'level_t-{char}'].attrs['class'] = clt


# calculate mats for talent
def update_talent(char, character, char_tracker):
	for t_c_t, t_t_t in [('talent_1_c', 'talent_1_t'),
						 ('talent_2_c', 'talent_2_t'),
						 ('talent_3_c', 'talent_3_t')]:
		t_c = character[t_c_t]
		t_t = character[t_t_t]
		if t_t > t_c:
			if 'selected' not in doc[f'{t_c_t}-{char}'].attrs['class']:
				doc[f'{t_c_t}-{char}'].attrs['class'] += ' selected'
				doc[f'{t_t_t}-{char}'].attrs['class'] += ' selected'

			if char == 'traveler_anemo' or (char == 'traveler_geo' and t_c_t == 'talent_1_c'):
				talent_prelookup = traveler['talent_1']
			elif char == 'traveler_geo':
				talent_prelookup = traveler['talent_2']
			else:
				talent_lookup = characters[char]['talent']

			for i in range(t_c + 1, t_t + 1):
				temp = costs['talent'][i]
				if 'traveler' in char:
					talent_lookup = talent_prelookup[i]
				grind_table_state['total']['mora'] += temp['mora']
				grind_table_state['total'][f"{talent_lookup['talent']}_{temp['talent'][1]}"] += temp['talent'][0]
				grind_table_state['total'][f"{talent_lookup['common']}_{temp['common'][1]}"] += temp['common'][0]
				grind_table_state['total'][talent_lookup['boss']] += temp['boss']
				grind_table_state['total']['crown'] += temp['crown']
				if temp['crown']:
					add_value_set(char_tracker, 'crown', char)
				if temp['mora']:
					add_value_set(char_tracker, 'mora', char)
				if temp['talent'][0]:
					add_value_set(char_tracker, talent_lookup['talent'], char)
				if temp['common'][0]:
					add_value_set(char_tracker, talent_lookup['common'], char)
				if temp['boss']:
					add_value_set(char_tracker, talent_lookup['boss'], char)

		elif 'selected' in doc[f'{t_c_t}-{char}'].attrs['class']:
			cl = doc[f'{t_c_t}-{char}'].attrs['class'].split()
			del cl[cl.index('selected')]
			clt = ' '.join(cl)
			doc[f'{t_c_t}-{char}'].attrs['class'] = clt
			doc[f'{t_t_t}-{char}'].attrs['class'] = clt


# calculate mats for weapon
def update_weapon(char, character, char_tracker):
	if character['weapon'] != '--':
		if 'selected' not in doc[f'weapon-{char}'].attrs['class']:
			doc[f'weapon-{char}'].attrs['class'] += ' selected'
		if character['weapon_t'] > character['weapon_c']:
			if 'selected' not in doc[f'weapon_c-{char}'].attrs['class']:
				doc[f'weapon_c-{char}'].attrs['class'] += ' selected'
				doc[f'weapon_t-{char}'].attrs['class'] += ' selected'

			weapon = weapons[characters[char]['weapon']][character['weapon']]
			for i in range(character['weapon_c'] + 1, character['weapon_t'] + 1):
				temp = costs[weapon['tier']][i]
				grind_table_state['total']['wep_xp'] += temp['xp']
				grind_table_state['total']['mora'] += temp['mora']
				grind_table_state['total'][f"{weapon['wam']}_{temp['wam'][1]}"] += temp['wam'][0]
				grind_table_state['total'][f"{weapon['common_rare']}_{temp['common_rare'][1]}"] += temp['common_rare'][0]
				grind_table_state['total'][f"{weapon['common']}_{temp['common'][1]}"] += temp['common'][0]
				if temp['xp']:
					add_value_set(char_tracker, 'wep_xp', char)
				if temp['mora']:
					add_value_set(char_tracker, 'mora', char)
				if temp['wam'][0]:
					add_value_set(char_tracker, weapon['wam'], char)
				if temp['common_rare'][0]:
					add_value_set(char_tracker, weapon['common_rare'], char)
				if temp['common'][0]:
					add_value_set(char_tracker, weapon['common'], char)
		elif 'selected' in doc[f'weapon_c-{char}'].attrs['class']:
			cl = doc[f'weapon_c-{char}'].attrs['class'].split()
			del cl[cl.index('selected')]
			clt = ' '.join(cl)
			doc[f'weapon_c-{char}'].attrs['class'] = clt
			doc[f'weapon_t-{char}'].attrs['class'] = clt
	elif 'selected' in doc[f'weapon-{char}'].attrs['class']:
		cl = doc[f'weapon-{char}'].attrs['class'].split()
		del cl[cl.index('selected')]
		clt = ' '.join(cl)
		doc[f'weapon-{char}'].attrs['class'] = clt


# Convert a number to an appropriate string
def readable_number(val):
	for num, fact, affix in [(100000, 6, 'm'),
							 (1000, 3, 'k')]:
		if val >= num:
			return f"{val/(10**fact):.1f}{affix}"
	return f"{val}"


# called when grind tracker needs to be updated
def calculate_change():
	if current_page == 'character':
		update_character()
	elif current_page == 'inventory':
		update_inventory()


# update displayed values on the inventory page
def update_inventory():
	# update inventory page
	for key in grind_table_state['total']:
		if '_sub_' in key:
			continue
		elif 'xp' == key:
			val = round(grind_table_state['total'][key] - grind_table_state['user'][key] - grind_table_state['user'][f"{key}_sub_1"] / 4 - grind_table_state['user'][f"{key}_sub_0"] / 20, 2)
		elif 'wep_xp' == key:
			val = round(grind_table_state['total'][key] - grind_table_state['user'][key] - grind_table_state['user'][f"{key}_sub_1"] / 5 - grind_table_state['user'][f"{key}_sub_0"] / 25, 2)
		else:
			val = grind_table_state['total'][key] - grind_table_state['user'][key]
		doc[f"{key}-total"].text = f"{grind_table_state['total'][key]:,}"
		doc[f"{key}-need"].text = f"{val if val > 0 else 0:,}"
		doc[f"{key}-need"].attrs['class'] = '' if val <= 0 else 'bad'

		if key[-1].isnumeric():
			root, num = key.rsplit('_', maxsplit=1)
			if val > 0 and int(num):  # last character is numeric and non-zero
				idx = int(num)-1
				newkey = f"{root}_{idx}"
				can_convert_up = (grind_table_state['user'][newkey] - grind_table_state['total'][newkey]) >= 3
				doc[f"{key}-need"].attrs['class'] = 'convert' if can_convert_up else 'bad'
			elif int(num) < len(strings[root])-1 and val <= -3:  # We have enough of this material to convert
				doc[f"{key}-need"].text = f" ({int((grind_table_state['total'][key] - grind_table_state['user'][key]) // -3):,})"
				# Only highlight green if item type is used in guide
				if any(grind_table_state['total'][f"{root}_{x}"] for x in range(0, len(strings[root]))):
					doc[f"{key}-need"].attrs['class'] = 'good'


# update diplayed values on the character page
def update_character():
	char_tracker = {}
	for val in grind_table_state['total']:
		grind_table_state['total'][val] = 0
	for char in grind_table_state['checked']:
		update_per_character(char, char_tracker)

	# Get a list of all chosen artifacts so we know what to farm
	for elt in doc.get(selector=f'.saved_arti'):
		char = elt.id.split('-')[1]
		if char in grind_table_state['checked'] and char in grind_table_state['arti_check']:
			add_value_set(char_tracker, elt.id.split('-')[-1], elt.id.split('-')[1])

	# adjust xp totals to units of their base type.
	grind_table_state['total']['mora'] += grind_table_state['total']['xp'] // 5
	grind_table_state['total']['xp'] = round(grind_table_state['total']['xp'] / 20000, 2)
	grind_table_state['total']['wep_xp'] = round(grind_table_state['total']['wep_xp'] / 10000, 2)

	# Build up and display farm table
	data = {
		'any': {0: {}, 20: {}, 40: {}, 60: {}},
		'mon': {},
		'tue': {},
		'wed': {},
		'thu': {},
		'fri': {},
		'sat': {},
		'sun': {},
	}
	resin = {
		'stormterror': 60,
		'wolf_of_the_north': 60,
		'golden_house': 60,
		'60_boss': 60,
		'40_boss': 40,
		'anemo_hypostasis': 40,
		'cryo_regisvine': 40,
		'electro_hypostasis': 40,
		'geo_hypostasis': 40,
		'oceanid': 40,
		'pyro_regisvine': 40,
		'clear_pool_and_mountain_cavern': 20,
		'domain_of_guyun': 20,
		'hidden_palace_of_zhou_formula': 20,
		'midsummer_courtyard': 20,
		'valley_of_remembrance': 20,
		'xp_leyline': 20,
		'mora_leyline': 20
	}
	arti_keys = [('arti', x) for x in char_tracker if x not in ingame_order]
	for section, item in [('base', 'xp'), ('base', 'wep_xp'), ('base', 'mora')] + ingame_order + arti_keys:
		if item in char_tracker:
			for day in farming_data[item]['when']:
				for loc in farming_data[item]['where']:
					if day == 'any':
						cost = 0 if loc not in resin else resin[loc]
						if loc not in data[day][cost]:
							data[day][cost][loc] = []
						data[day][cost][loc].append(item)
					else:
						if loc not in data[day]:
							data[day][loc] = []
						data[day][loc].append(item)

	d = SECTION(Class='grind')
	for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
		if data[day]:
			d <= H2([strings[day]])
			t = TABLE(TR(TH(strings["location"]) + TH(strings["item_s"]) + TH(strings["character_s"])), Class='borders body')
			for loc in sorted(data[day]):
				char_set = set()
				item_set = {}
				for x in data[day][loc]:
					if isinstance(strings[x], str) and grind_table_state['total'][x] - grind_table_state['user'][x] > 0:
						char_set.update(char_tracker[x])
						item_set[x] = {'text': strings[x], 'count': readable_number(grind_table_state['total'][x] - grind_table_state['user'][x])}
					else:
						for i in range(len(strings[x])):
							if grind_table_state['total'][f"{x}_{i}"] - grind_table_state['user'][f"{x}_{i}"] > 0:
								char_set.update(char_tracker[x])
								item_set[f"{x}_{i}"] = {'text': strings[x][i], 'count': readable_number(grind_table_state['total'][f"{x}_{i}"] - grind_table_state['user'][f"{x}_{i}"])}
				if item_set:
					v = (DIV(IMG(src=f"img/{x}.png", alt=item_set[x]['text'], title=item_set[x]['text']) + DIV(item_set[x]['count'], Class='bottom-right'), Class='container') for x in item_set)
					c = (IMG(src=f"img/{x}.png", alt=strings[x], title=strings[x]) for x in sorted(char_set))
					t <= TR(TD(strings[loc], Class="location") + TD(v) + TD(c))
			d <= t
	if any([data['any'][x] for x in [0, 20, 40, 60]]):
		d <= H2([strings['any']])
		for cost in [0, 20, 40, 60]:
			if data['any'][cost]:
				d <= H3(f"{cost} {strings['resin']}")
				t = TABLE(TR(TH(strings["location"]) + TH(strings["item_s"]) + TH(strings["character_s"])), Class='borders body')
				for loc in sorted(data['any'][cost]):
					char_set = set()
					item_set = {}
					for x in data['any'][cost][loc]:
						if isinstance(strings[x], str):
							if x in grind_table_state['total']:
								if 'xp' == x:
									val = int(grind_table_state['total'][x] - grind_table_state['user'][x] - grind_table_state['user'][f"{x}_sub_1"] / 4 - grind_table_state['user'][f"{x}_sub_0"] / 20 + .5)
								elif 'wep_xp' == x:
									val = int(grind_table_state['total'][x] - grind_table_state['user'][x] - grind_table_state['user'][f"{x}_sub_1"] / 5 - grind_table_state['user'][f"{x}_sub_0"] / 25 + .5)
								else:
									val = grind_table_state['total'][x] - grind_table_state['user'][x]

								if val > 0:
									char_set.update(char_tracker[x])
									item_set[x] = {'text': strings[x], 'count': readable_number(val)}
							else:
								char_set.update(char_tracker[x])
								item_set[x] = {'text': strings[x], 'count': ''}
						else:
							for i in range(len(strings[x])):
								if grind_table_state['total'][f"{x}_{i}"] - grind_table_state['user'][f"{x}_{i}"] > 0:
									char_set.update(char_tracker[x])
									item_set[f"{x}_{i}"] = {'text': strings[x][i], 'count': readable_number(grind_table_state['total'][f"{x}_{i}"] - grind_table_state['user'][f"{x}_{i}"])}
					if item_set:
						v = (DIV(IMG(src=f"img/{x}.png", alt=item_set[x]['text'], title=item_set[x]['text']) + DIV(item_set[x]['count'], Class='bottom-right'), Class='container') for x in item_set)
						c = (IMG(src=f"img/{x}.png", alt=strings[x], title=strings[x]) for x in sorted(char_set))
						t <= TR(TD(strings[loc], Class="location") + TD(v) + TD(c))
				d <= t

	doc['daily'].text = ''
	doc['daily'] <= d


def show_characters(ev):
	global current_page
	current_page = 'character'
	calculate_change()
	doc["inven"].style.display = 'none'
	doc["main"].style.display = 'block'
	doc["button_character"].attrs['class'] = 'current_tab'
	doc["button_inventory"].attrs['class'] = ''


def show_inventory(ev):
	global current_page
	current_page = 'inventory'
	calculate_change()
	doc["main"].style.display = 'none'
	doc["inven"].style.display = 'block'
	doc["button_inventory"].attrs['class'] = 'current_tab'
	doc["button_character"].attrs['class'] = ''


# Function for saving changes
@bind('.save', 'change')
def save_state(ev):
	key, char = ev.target.id.split('-')
	if ev.target.type == 'checkbox' and 'char_select' in ev.target.attrs['class']:
		binstate = ev.target.checked
		newstate = 'checked' if binstate else 'unchecked'
		for elt in doc.get(selector=f'TR[data-id="{ev.target.attrs["data-id"]}"]'):
			elt.attrs['class'] = newstate
		if ev.target.checked:
			grind_table_state['checked'].add(ev.target.id.split('-')[1])
			set_storage(ev.target.id, 'checked')
		else:
			grind_table_state['checked'].discard(ev.target.id.split('-')[1])
			del_storage(ev.target.id)
		calculate_change()
	elif ev.target.type == 'checkbox':
		if ev.target.checked:
			grind_table_state['arti_check'].add(ev.target.id.split('-')[1])
			del_storage(ev.target.id)
		else:
			grind_table_state['arti_check'].discard(ev.target.id.split('-')[1])
			set_storage(ev.target.id, 'unchecked')
		if char in grind_table_state['checked']:
			calculate_change()
	elif ev.target.type == 'select-one':
		if ev.target.selectedIndex:
			set_storage(ev.target.id, f"select-{ev.target.value}")
		else:
			del_storage(ev.target.id)
		grind_table_state['characters'][char][key] = int(ev.target.value) if ev.target.value.isnumeric() else ev.target.value
		if char in grind_table_state['checked']:
			calculate_change()
	elif ev.target.type == 'number':
		if not ev.target.value.isnumeric() or int(ev.target.value) < 0:
			ev.target.value = 0
		else:
			ev.target.value = int(ev.target.value)
		grind_table_state['user'][key] = int(ev.target.value)
		set_storage(ev.target.id, ev.target.value)
		calculate_change()
	else:
		print(f"Unhandled element type for storage: {ev.target.type}")


# Function to handle deleting artifacts
def delete_me(ev):
	del_storage(ev.target.id)
	del doc[ev.target.id]
	grind_table_state['artifacts'].discard(ev.target.id)
	if ev.target.id.split('-')[1] in grind_table_state['arti_check']:
		calculate_change()


# Handle mouse clicks when the custom menu is present
def custom_menu(ev):
	if 'data-id' in ev.target.attrs and 'menu-item' in ev.target.attrs['class'] and 'vertical-menu' in ev.target.attrs['class']:
		if f"{ev.target.attrs['data-id']}-{ev.target.id}" not in doc:
			b = BUTTON(strings[ev.target.id], Class=f'text_button saved_arti {ev.target.attrs["data-id"].split("-")[1]}', Id=f"{ev.target.attrs['data-id']}-{ev.target.id}", data_arti=ev.target.id)
			b.bind('click', delete_me)
			doc[ev.target.attrs["data-id"]] <= b
			grind_table_state['artifacts'].add(f"{ev.target.attrs['data-id']}-{ev.target.id}")
			set_storage(f"{ev.target.attrs['data-id']}-{ev.target.id}", 'y')
			if ev.target.attrs['data-id'].split('-')[1] in grind_table_state['arti_check']:
				calculate_change()
		ev.stopPropagation()
	if 'vertical-menu' in doc:
		del doc['vertical-menu']
	doc.unbind('mouseclick', custom_menu)


# Function for showing a list of artifacts on click
@bind('.arti_list', 'click')
def showartis(ev):
	if 'vertical-menu' in doc:
		del doc['vertical-menu']
	doc.unbind('mouseclick', custom_menu)

	ev.stopPropagation()
	# Set up artifact select
	arti = DIV(Id='vertical-menu', Class='vertical-menu')
	for art in artifacts:
		temp = DIV(strings[art], Id=art, data_id=ev.target.attrs["data-id"], Class='vertical-menu menu-item')
		temp.bind('click', custom_menu)
		arti <= temp
	arti.top = ev.y
	arti.left = ev.x
	doc <= arti
	doc.bind('click', custom_menu)


doc["button_character"] .bind("click", show_characters)
doc["button_inventory"].bind("click", show_inventory)
doc["reset_all"].bind("click", reset_data)
doc["reset_character"].bind("click", reset_character)
doc["reset_inventory"].bind("click", reset_inventory)

init_page()
del doc['loading']
