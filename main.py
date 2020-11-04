from browser import document as doc
from browser import bind
from browser.html import TABLE, TR, TH, TD, INPUT, SELECT, OPTION, DIV, BUTTON, SPAN, LI, H2, H3
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

	for key in storage.keys():
		if key.startswith(storage_key):
			del storage[key]


# generator to get all values in storage.  used during page load to set things up
def list_storage():
	for val in storage:
		if val.startswith(storage_key):
			yield val[len(storage_key) + 1:], storage[val]


def init_page():
	t = TABLE(Class='body')
	t <= TR(
		TH("Character", colspan=2) +
		TH("Level", colspan=2) +
		TH("Normal", colspan=2) +
		TH("Skill", colspan=2) +
		TH("Burst", colspan=2) +
		TH("Weapon", colspan=3) +
		TH("Artifacts", colspan=2)
	)
	t <= TR(
		TH() +
		TH("Name") +
		TH("Now") +
		TH("Goal") +
		TH("Now") +
		TH("Goal") +
		TH("Now") +
		TH("Goal") +
		TH("Now") +
		TH("Goal") +
		TH("") +
		TH("Now") +
		TH("Goal") +
		TH("") +
		TH("Click to remove")
	)
	for char in characters:
		# set up level select
		lvlc = SELECT(Id=f"level_c-{char}", Class=f"{char} save")
		lvlt = SELECT(Id=f"level_t-{char}", Class=f"{char} save")
		for lvl in [lvlc, lvlt]:
			for c, val in enumerate([1, 20, 40, 50, 60, 70, 80, 90]):
				lvl <= OPTION(f"{val}", value=c)
		# Set up talent select
		t1c = SELECT(Id=f"talent_1_c-{char}", Class=f"{char} save")
		t1t = SELECT(Id=f"talent_1_t-{char}", Class=f"{char} save")
		t2c = SELECT(Id=f"talent_2_c-{char}", Class=f"{char} save")
		t2t = SELECT(Id=f"talent_2_t-{char}", Class=f"{char} save")
		t3c = SELECT(Id=f"talent_3_c-{char}", Class=f"{char} save")
		t3t = SELECT(Id=f"talent_3_t-{char}", Class=f"{char} save")
		for st in [t1t, t1c, t2t, t2c, t3t, t3c]:
			for cost in costs['talent']:
				st <= OPTION(cost)
		# Set up weapon select
		ws = SELECT(Id=f"weapon-{char}", data_id=f"select-{char}", Class=f'weapon {char} save')
		ws <= OPTION('--')
		sort_dict_wep = {}
		for item in weapons[characters[char]['weapon']]:
			if weapons[characters[char]['weapon']][item]['wam'] != 'unk':
				sort_dict_wep[strings[item]] = item
			else:
				if f"missing-{item}" not in doc:
					doc['missing'] <= LI(strings[item], Id=f"missing-{item}")

		for k in sorted(sort_dict_wep):
			ws <= OPTION(k, value=sort_dict_wep[k])
		wlvlc = SELECT(Id=f"weapon_c-{char}", Class=f"{char} save")
		wlvlt = SELECT(Id=f"weapon_t-{char}", Class=f"{char} save")
		for lvl in [wlvlc, wlvlt]:
			for c, val in enumerate([1, 20, 40, 50, 60, 70, 80, 90]):
				lvl <= OPTION(f"{val}", value=c)
		# Create table row for character
		t <= TR(
			TD(INPUT(Id=f"check-{char}", type='checkbox', data_id=f"check-{char}", Class='char_select save')) +
			TD(strings[char]) +
			TD(lvlc) +
			TD(lvlt) +
			TD(t1c) +
			TD(t1t) +
			TD(t2c) +
			TD(t2t) +
			TD(t3c) +
			TD(t3t) +
			TD(ws) +
			TD(wlvlc) +
			TD(wlvlt) +
			TD(BUTTON("Add", Class='arti_list text_button', data_id=f"arti-{char}")) +
			TD(DIV(Id=f"arti-{char}", Class=f'arti_span'))
			,
			data_id=f"check-{char}", Class='unchecked', data_color=characters[char]['element']
		)

	doc['test'] <= t

	# Create a table of items we might need and store their ids in a lookup table
	# char xp, weapon xp, and mora
	t = TABLE()
	t_own = TABLE()
	t <= TR(TH("Item") + TH("Amount"))
	t <= TR(TD('Character XP') + TD('0', Id='xp-total'), Id='xp-total_row')
	t <= TR(TD('Weapon XP') + TD('0', Id='wep_xp-total'), Id='wep_xp-total_row')
	t <= TR(TD('Mora') + TD('0', Id='mora-total'), Id='mora-total_row')
	t_own <= TR(TH("Item") + TH("Need") + TH("Have") + TH("Missing"))
	t_own <= TR(TD('Character XP') + TD('0', Id='xp-total_req') + INPUT(Type='number', min='0', step="1", value='0', Id='xp-user', Class='save') + TD('0', Id='xp-need'))
	t_own <= TR(TD('Weapon XP') + TD('0', Id='wep_xp-total_req') + INPUT(Type='number', min='0', step="1", value='0', Id='wep_xp-user', Class='save') + TD('0', Id='wep_xp-need'))
	t_own <= TR(TD('Mora') + TD('0', Id='mora-total_req') + INPUT(Type='number', min='0', step="1", value='0', Id='mora-user', Class='save') + TD('0', Id='mora-need'))
	grind_table_state['id'][f"xp-total"] = 0
	grind_table_state['id'][f"wep_xp-total"] = 0
	grind_table_state['id'][f"mora-total"] = 0
	for section in ['common', 'common_rare', 'boss', 'element_2', 'element_1', 'talent', 'wam', 'local']:
		if section in ['boss', 'element_2', 'local']:
			for item in groups[section]:
				grind_table_state['id'][f"{item}-total"] = 0
				t <= TR(TD(strings[item]) + TD('0', Id=f"{item}-total"), Id=f"{item}-total_row")
				t_own <= TR(TD(strings[item]) + TD('0', Id=f"{item}-total_req") + INPUT(Type='number', min='0', step="1", value='0', Id=f"{item}-user", Class='save') + TD('0', Id=f"{item}-need", Class='good'))
		if section in ['element_1', 'common', 'common_rare', 'wam', 'talent']:
			for item in groups[section]:
				for i in range(len(strings[item])):
					grind_table_state['id'][f"{item}_{i}-total"] = 0
					t <= TR(TD(strings[item][i]) + TD('0', Id=f"{item}_{i}-total"), Id=f"{item}_{i}-total_row")
					t_own <= TR(TD(strings[item][i]) + TD('0', Id=f"{item}_{i}-total_req") + INPUT(Type='number', min='0', step="1", value='0', Id=f"{item}_{i}-user", Class='save') + TD('0', Id=f"{item}_{i}-need", Class='good'))
	doc['farm'] <= H2(strings['missing']) + t
	doc['inven'] <= t_own

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

	# hide empty grind table rows
	for val in grind_table_state['id']:
		if grind_table_state['id'][val] == 0:
			doc[f"{val}_row"].style.display = 'none'
	calculate_change()

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


# custom implementation of default dict for int
def add_value_int(i_dict, key, val):
	if key not in i_dict:
		i_dict[key] = val
	else:
		i_dict[key] += val


# called when anything in the selection table changes to update grind trackers
def calculate_change():
	totals = {}
	grind_daily_tracker = set()
	for char in grind_table_state['checked']:
		# calculate mats for level
		level_c = int(doc[f'level_c-{char}'].value)
		level_t = int(doc[f'level_t-{char}'].value)
		if level_t > level_c:
			for i in range(level_c+1, level_t+1):
				temp = costs['character'][i]
				add_value_int(totals, 'xp', temp['xp'])
				add_value_int(totals, 'mora', temp['mora'])
				add_value_int(totals, f"{characters[char]['ascension']['element_1']}_{temp['element_1'][1]}", temp['element_1'][0])
				add_value_int(totals, characters[char]['ascension']['element_2'], temp['element_2'])
				add_value_int(totals, characters[char]['ascension']['local'], temp['local'])
				add_value_int(totals, f"{characters[char]['ascension']['common']}_{temp['common'][1]}", temp['common'][0])

		# calculate mats for talent
		talent_1_c = int(doc[f'talent_1_c-{char}'].value)
		talent_1_t = int(doc[f'talent_1_t-{char}'].value)
		talent_2_c = int(doc[f'talent_2_c-{char}'].value)
		talent_2_t = int(doc[f'talent_2_t-{char}'].value)
		talent_3_c = int(doc[f'talent_3_c-{char}'].value)
		talent_3_t = int(doc[f'talent_3_t-{char}'].value)
		for t_c, t_t in [(talent_1_c, talent_1_t), (talent_2_c, talent_2_t), (talent_3_c, talent_3_t)]:
			if t_t > t_c:
				for i in range(t_c + 1, t_t + 1):
					temp = costs['talent'][i]
					add_value_int(totals, 'mora', temp['mora'])
					add_value_int(totals, f"{characters[char]['talent']['talent']}_{temp['talent'][1]}", temp['talent'][0])
					add_value_int(totals, f"{characters[char]['talent']['common']}_{temp['common'][1]}", temp['common'][0])
					add_value_int(totals, characters[char]['talent']['boss'], temp['boss'])
		# calculate mats for weapon
		weapon_c = int(doc[f'weapon_c-{char}'].value)
		weapon_t = int(doc[f'weapon_t-{char}'].value)
		if weapon_t > weapon_c:
			weapon = weapons[characters[char]['weapon']][doc[f'weapon-{char}'].value]
			for i in range(weapon_c + 1, weapon_t + 1):
				temp = costs[weapon['tier']][i]
				add_value_int(totals, 'wep_xp', temp['xp'])
				add_value_int(totals, 'mora', temp['mora'])
				add_value_int(totals, f"{weapon['wam']}_{temp['wam'][1]}", temp['wam'][0])
				add_value_int(totals, f"{weapon['common_rare']}_{temp['common_rare'][1]}", temp['common_rare'][0])
				add_value_int(totals, f"{weapon['common']}_{temp['common'][1]}", temp['common'][0])

	# Get a list of all chosen artifacts so we know what to farm
	for elt in doc.get(selector=f'.saved_arti'):
		if elt.id.split('-')[1] in grind_table_state['checked']:
			grind_daily_tracker.add(elt.id.split('-')[-1])

	for item in grind_table_state['id']:
		key = item.split('-')[0]
		if key in totals:
			new_val = totals[key]-int(doc[f'{key}-user'].value)
			grind_table_state['id'][item] = new_val
			doc[item].text = f"{new_val:,}"
			doc[f"{key}-total_req"].text = f"{totals[key]:,}"
			doc[f"{key}-need"].text = f"{new_val:,}"
			doc[f"{key}-need"].attrs['class'] = 'bad' if new_val > 0 else 'good'
			if new_val > 0:
				grind_daily_tracker.add(key[:-2] if key[-1].isnumeric() else key)
				doc[f"{item}_row"].style.display = 'table-row'
			else:
				doc[f"{item}_row"].style.display = 'none'
		elif grind_table_state['id'][item] > 0:
			grind_table_state['id'][item] = 0
			doc[f"{key}-total_req"].text = "0"
			doc[f"{key}-need"].text = f"{-int(doc[f'{key}-user'].value):,}"
			doc[item].text = "0"
			doc[f"{item}_row"].style.display = 'none'
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
			t = TABLE(TR(TH("Location") + TH("Item(s)")))
			for loc in sorted(data[day]):
				t <= TR(TD(strings[loc]) + TD(', '.join([strings[x] if isinstance(strings[x], str) else strings[x][0] for x in data[day][loc]])))
			doc['daily'] <= t
	if any([data['any'][x] for x in [0, 20, 40, 60]]):
		doc['daily'] <= H2([strings['any']])
		for cost in [0, 20, 40, 60]:
			if data['any'][cost]:
				doc['daily'] <= H3(f"{cost} {strings['resin']}")
				t = TABLE(TR(TH("Location") + TH("Item(s)")))
				for loc in sorted(data['any'][cost]):
					t <= TR(TD(strings[loc]) + TD(', '.join([strings[x] if isinstance(strings[x], str) else strings[x][0] for x in data['any'][cost][loc]])))
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
	else:
		if 'vertical-menu' in doc:
			del doc['vertical-menu']
		doc.unbind('mouseclick', custom_menu)


def show_characters(ev):
	doc["inven"].style.display = 'none'
	doc["main"].style.display = 'block'


def show_inventory(ev):
	doc["main"].style.display = 'none'
	doc["inven"].style.display = 'block'


b_char = BUTTON("Characters")
b_char.bind("click", show_characters)
doc["character"] <= b_char
b_inven = BUTTON("Inventory")
b_inven.bind("click", show_inventory)
doc["inventory"] <= b_inven
b_reset = BUTTON("Reset Data")
b_reset.bind("click", reset_data)
doc["reset"] <= b_reset
init_page()
del doc['loading']

