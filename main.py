from browser import document as doc
from browser import bind
from browser.html import TABLE, TR, TH, TD, INPUT, SELECT, OPTION, DIV, BUTTON, SPAN, LI, H2, H3, IMG, COLGROUP, COL
from browser.local_storage import storage

from characters import characters
from weapons import weapons
from artifacts import artifacts
from lang_en import strings
from costs import costs
from farming_data import farming_data
from groups import groups


storage_key = "genshin_grind_planner"
# dict to store states for the grind table to detect changes in selection table
grind_table_state = {'checked': set(), 'id': {}}


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
	for elt in doc.get(selector='input[type=checkbox]'):
		doc[elt.id].checked = False
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
	for elt in doc.get(selector='input[type=checkbox]'):
		doc[elt.id].checked = False
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


def init_page():
	grind_table_state['id'][f"xp-total"] = 0
	grind_table_state['id'][f"wep_xp-total"] = 0
	grind_table_state['id'][f"mora-total"] = 0
	for section in groups:
		if section in ['boss', 'element_2', 'local']:
			for item in groups[section]:
				grind_table_state['id'][f"{item}-total"] = 0
		if section in ['element_1', 'common', 'common_rare', 'wam', 'talent']:
			for item in groups[section]:
				for i in range(len(strings[item])-1, -1, -1):
					grind_table_state['id'][f"{item}_{i}-total"] = 0

	for k, v in list_storage():
		if v == 'checked':
			grind_table_state['checked'].add(k.split('-')[1])
			doc[k].checked = True
			for elt in doc.get(selector=f'TR[data-id="{k}"]'):
				elt.attrs['class'] = 'checked'
		elif 'select' in v:
			doc[k].value = v.split('-')[1]
		elif v == 'y':
			idx = k.rfind('-')
			target = k[:idx]
			ev_id = k[idx+1:]
			b = BUTTON(strings[ev_id], Class=f'text_button saved_arti {target.split("-")[1]}', Id=f"{target}-{ev_id}", data_arti=ev_id)
			b.bind('click', delete_me)
			doc[target] <= b
		elif '-user' in k:
			doc[k].value = v
		else:
			print(f"Invalid stored data: {k}, {v}")

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


# called when anything in the selection table changes to update grind trackers
def calculate_change():
	totals = {}
	grind_daily_tracker = set()
	char_tracker = {}
	for char in grind_table_state['checked']:
		# calculate mats for level
		level_c = int(doc[f'level_c-{char}'].value)
		level_t = int(doc[f'level_t-{char}'].value)
		if level_t > level_c:
			if 'good' not in doc[f'level_c-{char}'].attrs['class']:
				doc[f'level_c-{char}'].attrs['class'] += ' good'
				doc[f'level_t-{char}'].attrs['class'] += ' good'
			for i in range(level_c+1, level_t+1):
				temp = costs['character'][i]
				add_value_int(totals, 'xp', temp['xp'])
				add_value_int(totals, 'mora', temp['mora'])
				add_value_int(totals, f"{characters[char]['ascension']['element_1']}_{temp['element_1'][1]}", temp['element_1'][0])
				add_value_int(totals, characters[char]['ascension']['element_2'], temp['element_2'])
				add_value_int(totals, characters[char]['ascension']['local'], temp['local'])
				add_value_int(totals, f"{characters[char]['ascension']['common']}_{temp['common'][1]}", temp['common'][0])
				if temp['element_1'][0]:
					add_value_set(char_tracker, characters[char]['ascension']['element_1'], char)
				if temp['element_2']:
					add_value_set(char_tracker, characters[char]['ascension']['element_2'], char)
				if temp['local']:
					add_value_set(char_tracker, characters[char]['ascension']['local'], char)
				if temp['common'][0]:
					add_value_set(char_tracker, characters[char]['ascension']['common'], char)
		elif 'good' in doc[f'level_c-{char}'].attrs['class']:
			cl = doc[f'level_c-{char}'].attrs['class'].split()
			del cl[cl.index('good')]
			clt = ' '.join(cl)
			doc[f'level_c-{char}'].attrs['class'] = clt
			doc[f'level_t-{char}'].attrs['class'] = clt

		# calculate mats for talent
		for t_c_e, t_t_e in [(doc[f'talent_1_c-{char}'], doc[f'talent_1_t-{char}']),
							 (doc[f'talent_2_c-{char}'], doc[f'talent_2_t-{char}']),
							 (doc[f'talent_3_c-{char}'], doc[f'talent_3_t-{char}'])]:
			t_c = int(t_c_e.value)
			t_t = int(t_t_e.value)
			if t_t > t_c:
				if 'good' not in t_c_e.attrs['class']:
					t_c_e.attrs['class'] += ' good'
					t_t_e.attrs['class'] += ' good'

				for i in range(t_c + 1, t_t + 1):
					temp = costs['talent'][i]
					add_value_int(totals, 'mora', temp['mora'])
					add_value_int(totals, f"{characters[char]['talent']['talent']}_{temp['talent'][1]}", temp['talent'][0])
					add_value_int(totals, f"{characters[char]['talent']['common']}_{temp['common'][1]}", temp['common'][0])
					add_value_int(totals, characters[char]['talent']['boss'], temp['boss'])
					if temp['talent'][0]:
						add_value_set(char_tracker, characters[char]['talent']['talent'], char)
					if temp['common'][0]:
						add_value_set(char_tracker, characters[char]['talent']['common'], char)
					if temp['boss']:
						add_value_set(char_tracker, characters[char]['talent']['boss'], char)
			elif 'good' in t_c_e.attrs['class']:
				cl = t_c_e.attrs['class'].split()
				del cl[cl.index('good')]
				clt = ' '.join(cl)
				t_c_e.attrs['class'] = clt
				t_t_e.attrs['class'] = clt

		# calculate mats for weapon
		if doc[f'weapon-{char}'].value != '--':
			weapon_c = int(doc[f'weapon_c-{char}'].value)
			weapon_t = int(doc[f'weapon_t-{char}'].value)
			if weapon_t > weapon_c:
				if 'good' not in doc[f'weapon_c-{char}'].attrs['class']:
					doc[f'weapon_c-{char}'].attrs['class'] += ' good'
					doc[f'weapon_t-{char}'].attrs['class'] += ' good'

				weapon = weapons[characters[char]['weapon']][doc[f'weapon-{char}'].value]
				for i in range(weapon_c + 1, weapon_t + 1):
					temp = costs[weapon['tier']][i]
					add_value_int(totals, 'wep_xp', temp['xp'])
					add_value_int(totals, 'mora', temp['mora'])
					add_value_int(totals, f"{weapon['wam']}_{temp['wam'][1]}", temp['wam'][0])
					add_value_int(totals, f"{weapon['common_rare']}_{temp['common_rare'][1]}", temp['common_rare'][0])
					add_value_int(totals, f"{weapon['common']}_{temp['common'][1]}", temp['common'][0])
					if temp['wam'][0]:
						add_value_set(char_tracker, weapon['wam'], char)
					if temp['common_rare'][0]:
						add_value_set(char_tracker, weapon['common_rare'], char)
					if temp['common'][0]:
						add_value_set(char_tracker, weapon['common'], char)
			elif 'good' in doc[f'weapon_c-{char}'].attrs['class']:
				cl = doc[f'weapon_c-{char}'].attrs['class'].split()
				del cl[cl.index('good')]
				clt = ' '.join(cl)
				doc[f'weapon_c-{char}'].attrs['class'] = clt
				doc[f'weapon_t-{char}'].attrs['class'] = clt

	# Get a list of all chosen artifacts so we know what to farm
	for elt in doc.get(selector=f'.saved_arti'):
		if elt.id.split('-')[1] in grind_table_state['checked']:
			grind_daily_tracker.add(elt.id.split('-')[-1])
			add_value_set(char_tracker, elt.id.split('-')[-1], elt.id.split('-')[1])

	if 'xp' in totals:
		totals['xp'] = (totals['xp'] + 10000) // 20000
	if 'wep_xp' in totals:
		totals['wep_xp'] = (totals['wep_xp'] + 5000) // 10000

	for item in grind_table_state['id']:
		key = item.split('-')[0]
		if key in totals:
			new_val = totals[key]-int(doc[f'{key}-user'].value)
			new_val = new_val if new_val > 0 else 0
			grind_table_state['id'][item] = new_val
			doc[item].text = f"{new_val:,}"
			doc[f"{key}-total"].text = f"{totals[key]:,}"
			doc[f"{key}-need"].text = f"{new_val:,}"
			doc[f"{key}-need"].attrs['class'] = 'bad' if new_val else 'good'
			if new_val:
				grind_daily_tracker.add(key[:-2] if key[-1].isnumeric() else key)
		elif grind_table_state['id'][item] > 0:
			grind_table_state['id'][item] = 0
			doc[f"{key}-total"].text = "0"
			doc[f"{key}-need"].text = f"{-int(doc[f'{key}-user'].value):,}"
			doc[item].text = "0"
	grind_daily_tracker.discard('xp')
	grind_daily_tracker.discard('wep_xp')
	grind_daily_tracker.discard('mora')
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
	}
	for item in grind_daily_tracker:
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
	doc['daily'].text = ''
	for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
		if data[day]:
			doc['daily'] <= H2([strings[day]])
			t = TABLE(TR(TH("Location") + TH("Item(s)") + TH("Character(s)")), Class='borders')
			for loc in sorted(data[day]):
				new_set = {y for x in data[day][loc] for y in char_tracker[x]}
				v = (IMG(src=f"img/{x}.png", alt=(strings[x] if isinstance(strings[x], str) else strings[x][0]), title=(strings[x] if isinstance(strings[x], str) else strings[x][0])) for x in data[day][loc])
				c = (IMG(src=f"img/{x}.png", alt=strings[x], title=strings[x]) for x in sorted(new_set))
				t <= TR(TD(strings[loc]) + TD(v) + TD(c))
			doc['daily'] <= t
	if any([data['any'][x] for x in [0, 20, 40, 60]]):
		doc['daily'] <= H2([strings['any']])
		for cost in [0, 20, 40, 60]:
			if data['any'][cost]:
				doc['daily'] <= H3(f"{cost} {strings['resin']}")
				t = TABLE(TR(TH("Location") + TH("Item(s)") + TH("Character(s)")), Class='borders')
				for loc in sorted(data['any'][cost]):
					new_set = {y for x in data['any'][cost][loc] for y in char_tracker[x]}
					v = (IMG(src=f"img/{x}.png", alt=(strings[x] if isinstance(strings[x], str) else strings[x][0]), title=(strings[x] if isinstance(strings[x], str) else strings[x][0])) for x in data['any'][cost][loc])
					c = (IMG(src=f"img/{x}.png", alt=strings[x], title=strings[x]) for x in sorted(new_set))
					t <= TR(TD(strings[loc]) + TD(v) + TD(c))
				doc['daily'] <= t


# Function to handle deleting artifacts
def delete_me(ev):
	del_storage(ev.target.id)
	del doc[ev.target.id]
	calculate_change()


# Handle mouse clicks when the custom menu is present
def custom_menu(ev):
	if 'data-id' in ev.target.attrs and 'menu-item' in ev.target.attrs['class'] and 'vertical-menu' in ev.target.attrs['class']:
		if f"{ev.target.attrs['data-id']}-{ev.target.id}" not in doc:
			b = BUTTON(strings[ev.target.id], Class=f'text_button saved_arti {ev.target.attrs["data-id"].split("-")[1]}', Id=f"{ev.target.attrs['data-id']}-{ev.target.id}", data_arti=ev.target.id)
			b.bind('click', delete_me)
			doc[ev.target.attrs["data-id"]] <= b
			set_storage(f"{ev.target.attrs['data-id']}-{ev.target.id}", 'y')
			calculate_change()

		ev.stopPropagation()
	if 'vertical-menu' in doc:
		del doc['vertical-menu']
	doc.unbind('mouseclick', custom_menu)


def show_characters(ev):
	doc["inven"].style.display = 'none'
	doc["main"].style.display = 'block'
	doc["button_character"].attrs['class'] = 'current_tab'
	doc["button_inventory"].attrs['class'] = ''


def show_inventory(ev):
	doc["main"].style.display = 'none'
	doc["inven"].style.display = 'block'
	doc["button_inventory"].attrs['class'] = 'current_tab'
	doc["button_character"].attrs['class'] = ''


# Function for saving changes
@bind('.save', 'change')
def save_state(ev):
	if ev.target.type == 'checkbox':
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
	elif ev.target.type == 'select-one':
		if ev.target.selectedIndex:
			set_storage(ev.target.id, f"select-{ev.target.value}")
		else:
			del_storage(ev.target.id)
	elif ev.target.type == 'number':
		if not ev.target.value.isnumeric() or int(ev.target.value) < 0:
			ev.target.value = 0
		else:
			ev.target.value = int(ev.target.value)
		set_storage(ev.target.id, ev.target.value)
	else:
		print(f"Unhandled element type for storage: {ev.target.type}")
	calculate_change()


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
doc["reset"].bind("click", reset_data)
doc["reset"].bind("click", reset_character)
doc["reset"].bind("click", reset_inventory)

init_page()
del doc['loading']

