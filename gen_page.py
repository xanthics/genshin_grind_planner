from browser import document as doc
from browser.html import TABLE, TR, TH, TD, INPUT, SELECT, OPTION, DIV, BUTTON, SPAN, LI, H2, H3, IMG, COLGROUP, COL, P, SECTION, BR

from characters import characters
from weapons import weapons
from lang_en import strings
from costs import costs
from ingame_order import ingame_order
from traveler import traveler, traveler_talent


# Create the static elements of the home page
def init_page():
	init_characters()
	init_inventory()
	init_show_hide()
	init_information()


# Show various useful information
def init_information():
	order_index = [x[1] for x in ingame_order]
	data = {k: set() for k in order_index}
	char_data = {}
	# iterate all the characters and add items they need to data
	for character in characters:
		char_data[character] = set()
		for field in characters[character]:
			# keys with subkeys
			if field in ['ascension', 'talent']:
				for key in characters[character][field]:
					val = characters[character][field][key]
					if val in data:
						data[val].add(character)
						char_data[character].add(val)
			else:
				val = characters[character][field]
				if val in data:
					data[val].add(character)
					char_data[character].add(val)
	trav_data = {}
	# do the same thing for traveler talents
	for tal_group in traveler:
		trav_data[tal_group] = set()
		for row in traveler[tal_group]:
			for field in row:
				trav_data[tal_group].add(row[field])
	for t_char in traveler_talent:
		char_data[t_char] = set()
		for talent in traveler_talent[t_char]:
			for item in trav_data[talent]:
				data[item].add(t_char)
				char_data[t_char].add(item)
	# create a table with the character->item dictionary we just built
	t_chars = TABLE(TR(TH(strings["character"]) + TH(strings["item_s"])), Class='borders body')
	for char in sorted(char_data):
		item_set = {}
		for item in char_data[char]:
			if item in strings:
				i_idx = order_index.index(item)
				if isinstance(strings[item], list):
					c = len(strings[item]) - 1
					item_set[i_idx] = [f"{item}_{c}", strings[item][c]]
				else:
					item_set[i_idx] = [item, strings[item]]
		i = (IMG(src=f"img/{item_set[x][0]}.png", alt=item_set[x][1], title=item_set[x][1]) for x in sorted(item_set))
		c = IMG(src=f"img/{char}.png", alt=strings[char], title=strings[char])
		t_chars <= TR(TD(c) + TD(i))
	# create a table with the item->character dictionary we just built
	t_items = TABLE(TR(TH(strings["item_s"]) + TH(strings["character_s"])), Class='borders body')
	for typ, item in ingame_order:
		if item in data:
			if data[item]:  # only show items used by a character
				if isinstance(strings[item], list):
					i = (IMG(src=f"img/{item}_{c}.png", alt=strings[item][c], title=strings[item][c]) for c in range(len(strings[item])))
				else:
					i = IMG(src=f"img/{item}.png", alt=strings[item], title=strings[item])
				c = (IMG(src=f"img/{x}.png", alt=strings[x], title=strings[x]) for x in sorted(data[item]))
				t_items <= TR(TD(i) + TD(c))

	doc['information'] <= SECTION(P(strings['character_mats']) + t_chars + BR()+ BR() + t_items, Class='grind')


# Initialize select boxes so you can only have certain characters show
def init_show_hide():
	# initialize options
	element = set()
	weapon = set()
	for char in characters:
		if char == 'traveler':
			continue
		element.add(characters[char]['element'])
		weapon.add(characters[char]['weapon'])
	# selected
	cst = SELECT(Id=f"selected", Class=f"save onehundred")
	for s in ['any', 'checked', 'unchecked']:
		cst <= OPTION(s.capitalize(), value=s)
	# element
	est = SELECT(Id=f"element", Class=f"save onehundred")
	for s in ['any'] + sorted(element):
		est <= OPTION(s.capitalize(), value=s)
	# weapon
	wst = SELECT(Id=f"weapon", Class=f"save onehundred")
	for s in ['any'] + sorted(weapon):
		wst <= OPTION(s.capitalize(), value=s)

	t = TABLE(TR(TH() + TH('Option')))
	t <= TR(TD('Character') + TD(cst))
	t <= TR(TD('Element') + TD(est))
	t <= TR(TD('Weapon') + TD(wst))

	doc['show_hide'] <= t + P("Note that all selections have to be true for a character to be visible.")


def init_characters():
	t = TABLE(Class='body')
	t <= COLGROUP(
		COL() +
		COL() +
		COL(Class='left_border') +
		COL(Class='left_dotted') +
		COL(Class='left_border') +
		COL(Class='left_dotted') +
		COL(Class='left_border') +
		COL(Class='left_dotted') +
		COL(Class='left_border') +
		COL(Class='left_dotted') +
		COL(Class='left_border') +
		COL(Class='left_dotted') +
		COL(Class='left_dotted') +
		COL(Class='left_border') +
		COL(Class='left_dotted') +
		COL(Class='left_dotted')
	)
	t <= TR(
		TH(strings["character"], colspan=2) +
		TH(strings["level"], colspan=2) +
		TH(strings["normal"], colspan=2) +
		TH(strings["skill"], colspan=2) +
		TH(strings["burst"], colspan=2) +
		TH(strings["weapon"], colspan=3) +
		TH(strings["artifacts"], colspan=3)
	)
	t <= TR(
		TH() +
		TH(strings["name"]) +
		TH(strings["now"]) +
		TH(strings["goal"]) +
		TH(strings["now"]) +
		TH(strings["goal"]) +
		TH(strings["now"]) +
		TH(strings["goal"]) +
		TH(strings["now"]) +
		TH(strings["goal"]) +
		TH() +
		TH(strings["now"]) +
		TH(strings["goal"]) +
		TH(strings["click_to_remove"], colspan=3)
	)
	for char in sorted(characters):
		if char == 'traveler':
			continue
		# set up level select
		lvlc = SELECT(Id=f"level_c-{char}", Class=f"{char} save")
		lvlt = SELECT(Id=f"level_t-{char}", Class=f"{char} save")
		for lvl in [lvlc, lvlt]:
			for c, val in [(0, "1"),
						   (1, "20"), (11, "20 A"),
						   (2, "40"), (12, "40 A"),
						   (3, "50"), (13, "50 A"),
						   (4, "60"), (14, "60 A"),
						   (5, "70"), (15, "70 A"),
						   (6, "80"), (16, "80 A"),
						   (7, "90")]:
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
		ws <= OPTION('--', value='--')
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
			for c, val in [(0, "1"),
						   (1, "20"), (11, "20 A"),
						   (2, "40"), (12, "40 A"),
						   (3, "50"), (13, "50 A"),
						   (4, "60"), (14, "60 A"),
						   (5, "70"), (15, "70 A"),
						   (6, "80"), (16, "80 A"),
						   (7, "90")]:
				lvl <= OPTION(f"{val}", value=c)
		# Create table row for character
		t <= TR(
			TD(INPUT(Id=f"check-{char}", type='checkbox', data_id=f"check-{char}", Class='char_select save')) +
			TD(IMG(src=f"img/{char}.png", alt=strings[char], title=strings[char])) +
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
			TD(INPUT(Id=f"use_arti-{char}", type='checkbox', Class='save', checked='checked')) +
			TD(BUTTON(strings["add"], Class='arti_list text_button', data_id=f"arti-{char}")) +
			TD(DIV(Id=f"arti-{char}", Class=f'arti_span'))
			,
			data_id=f"check-{char}", Class='unchecked', data_color=characters[char]['element'], data_weapon=characters[char]['weapon']
		)
	# set up traveler base row
	# set up level select
	char = 'traveler'
	lvlc = SELECT(Id=f"level_c-{char}", Class=f"{char} save")
	lvlt = SELECT(Id=f"level_t-{char}", Class=f"{char} save")
	for lvl in [lvlc, lvlt]:
		for c, val in [(0, "1"),
					   (1, "20"), (11, "20 A"),
					   (2, "40"), (12, "40 A"),
					   (3, "50"), (13, "50 A"),
					   (4, "60"), (14, "60 A"),
					   (5, "70"), (15, "70 A"),
					   (6, "80"), (16, "80 A"),
					   (7, "90")]:
			lvl <= OPTION(f"{val}", value=c)
	# Set up weapon select
	ws = SELECT(Id=f"weapon-{char}", data_id=f"select-{char}", Class=f'weapon {char} save')
	ws <= OPTION('--', value='--')
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
		for c, val in [(0, "1"),
					   (1, "20"), (11, "20 A"),
					   (2, "40"), (12, "40 A"),
					   (3, "50"), (13, "50 A"),
					   (4, "60"), (14, "60 A"),
					   (5, "70"), (15, "70 A"),
					   (6, "80"), (16, "80 A"),
					   (7, "90")]:
			lvl <= OPTION(f"{val}", value=c)
	# Create table row for character
	t <= TR(
		TD(INPUT(Id=f"check-{char}", type='checkbox', data_id=f"check-{char}", Class='char_select save')) +
		TD(IMG(src=f"img/{char}.png", alt=strings[char], title=strings[char])) +
		TD(lvlc) +
		TD(lvlt) +
		TD() +
		TD() +
		TD() +
		TD() +
		TD() +
		TD() +
		TD(ws) +
		TD(wlvlc) +
		TD(wlvlt) +
		TD(INPUT(Id=f"use_arti-{char}", type='checkbox', Class='save', checked='checked')) +
		TD(BUTTON(strings["add"], Class='arti_list text_button', data_id=f"arti-{char}")) +
		TD(DIV(Id=f"arti-{char}", Class=f'arti_span'))
		,
		data_id=f"check-{char}", Class='unchecked', data_color='multi', data_weapon=characters[char]['weapon']
	)
	# set up traveler anemo/geo row
	for char in sorted(traveler_talent):
		ele = char.split('_')[1]
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
		# Create table row for character
		t <= TR(
			TD(INPUT(Id=f"check-{char}", type='checkbox', data_id=f"check-{char}", Class='char_select save')) +
			TD(IMG(src=f"img/{char}.png", alt=strings['traveler'], title=strings['traveler'])) +
			TD() +
			TD() +
			TD(t1c) +
			TD(t1t) +
			TD(t2c) +
			TD(t2t) +
			TD(t3c) +
			TD(t3t) +
			TD() +
			TD() +
			TD() +
			TD() +
			TD() +
			TD()
			,
			data_id=f"check-{char}", Class='unchecked', data_color=ele, data_weapon=characters['traveler']['weapon']
		)
	doc['character_list'] <= t


def init_inventory():
	# Create a table of items we might need and store their ids in a lookup table
	# char xp, weapon xp, and mora
	t_own = TABLE(Class='borders center')
	t_own <= TR(TH(strings["item"]) + TH(strings["need"]) + TH(strings["have"]) + TH(strings["missing_"]))
	t_own <= TR(TD(IMG(src=f"img/wep_xp.png", alt=strings['wep_xp'], title=strings['wep_xp'])) + TD('0', Id='wep_xp-total') + TD(INPUT(Type='number', min='0', step="1", value='0', Id='wep_xp-user', Class='save')) + TD('0', Id='wep_xp-need', Class='good'))
	t_own <= TR(TD(IMG(src=f"img/wep_xp_sub_1.png", alt=strings['wep_xp'], title=strings['wep_xp'])) + TD() + TD(INPUT(Type='number', min='0', step="1", value='0', Id='wep_xp_sub_1-user', Class='save')) + TD())
	t_own <= TR(TD(IMG(src=f"img/wep_xp_sub_0.png", alt=strings['wep_xp'], title=strings['wep_xp'])) + TD() + TD(INPUT(Type='number', min='0', step="1", value='0', Id='wep_xp_sub_0-user', Class='save')) + TD())
	t_own <= TR(TD(IMG(src=f"img/mora.png", alt=strings['mora'], title=strings['mora'])) + TD('0', Id='mora-total') + TD(INPUT(Type='number', min='0', step="1", value='0', Id='mora-user', Class='save')) + TD('0', Id='mora-need', Class='good'))
	t_own <= TR(TD(IMG(src=f"img/xp.png", alt=strings['xp'], title=strings['xp'])) + TD('0', Id='xp-total') + TD(INPUT(Type='number', min='0', step="1", value='0', Id='xp-user', Class='save')) + TD('0', Id='xp-need', Class='good'))
	t_own <= TR(TD(IMG(src=f"img/xp_sub_1.png", alt=strings['xp'], title=strings['xp'])) + TD() + TD(INPUT(Type='number', min='0', step="1", value='0', Id='xp_sub_1-user', Class='save')) + TD())
	t_own <= TR(TD(IMG(src=f"img/xp_sub_0.png", alt=strings['xp'], title=strings['xp'])) + TD() + TD(INPUT(Type='number', min='0', step="1", value='0', Id='xp_sub_0-user', Class='save')) + TD())
	doc['inventory'] <= P(strings['convert_notice']) + t_own

	width = 3
	alt_width = 2
	row = 0
	prev_section = "init"
	t_own = TABLE(Class='borders center spacer')
	t_head = TR()
	for c in range(width):
		t_head <= TH(strings["item"]) + TH(strings["need"]) + TH(strings["have"]) + TH(strings["missing_"])
		if c < width - 1:
			t_head <= TH(Class="spacer")
	c = 0
	t_own <= t_head
	t_row = TR(Class='tr_odd')
	lookup = {0: 14, 1: 9, 2: 4, 3: 0}
	for section, item in ingame_order:
		if section != prev_section:
			if c % width:
				if lookup[c]:
					t_row <= TD(colspan=lookup[c], Class='notvis')
				t_own <= t_row
				t_row = TR(Class='tr_odd' if row % 2 else 'tr_even')
				row += 1
				c = 0
			if prev_section != 'init':
				c = 0
				t_own <= TR(TD(colspan=14), Class='empty_row')
			prev_section = section
		if section in ['element_1', 'common', 'common_rare', 'wam', 'talent']:
			if section in ['element_1', 'wam']:
				if c:
					if lookup[c]:
						t_row <= TD(colspan=lookup[c], Class='notvis')
					t_own <= t_row
					t_row = TR(Class='tr_odd' if row % 2 else 'tr_even')
					row += 1
					c = 0
				t_width = alt_width
			else:
				t_width = width
			prev_section = 'end section'
			for i in range(len(strings[item])-1, -1, -1):
				t_td = TD(IMG(src=f"img/{item}_{i}.png", alt=strings[item][i], title=strings[item][i])) + TD('0', Id=f"{item}_{i}-total") + TD(INPUT(Type='number', min='0', step="1", value='0', Id=f"{item}_{i}-user", Class='save')) + TD('0', Id=f"{item}_{i}-need")
				c += 1
				t_row <= t_td
				if not (c % t_width):
					if lookup[c]:
						t_row <= TD(colspan=lookup[c] if t_width == 3 else lookup[c] + 1, Class='notvis')
					t_own <= t_row
					t_row = TR(Class='tr_odd' if row % 2 else 'tr_even')
					c = 0
					row += 1
				elif c % width < width:
					t_row <= TD()
		else:  # section in ['boss', 'element_2', 'local', 'special']:
			t_td = TD(IMG(src=f"img/{item}.png", alt=strings[item], title=strings[item])) + TD('0', Id=f"{item}-total") + TD(INPUT(Type='number', min='0', step="1", value='0', Id=f"{item}-user", Class='save')) + TD('0', Id=f"{item}-need")
			c += 1
			t_row <= t_td
			if not (c % width):
				if lookup[c]:
					t_row <= TD(colspan=lookup[c], Class='notvis')
				t_own <= t_row
				t_row = TR(Class='tr_odd' if row % 2 else 'tr_even')
				row += 1
				c = 0
			elif c % width < width:
				t_row <= TD()

	if c % width:
		if lookup[c]:
			t_row <= TD(colspan=lookup[c], Class='notvis')
		t_own <= t_row

	doc['inventory'] <= t_own

	b_reset = BUTTON(strings["reset_all_data"], Id='reset_all')
	doc["reset"] <= b_reset

	b_reset = BUTTON(strings["reset_character"], Id='reset_character')
	doc["reset"] <= b_reset

	b_reset = BUTTON(strings["reset_inventory"], Id='reset_inventory')
	doc["reset"] <= b_reset


init_page()
doc['loading'] <= DIV(Id='prerendered')
