from browser import document as doc
from browser.html import TABLE, TR, TH, TD, INPUT, SELECT, OPTION, DIV, BUTTON, SPAN, LI, H2, H3, IMG, COLGROUP, COL, P

from characters import characters
from weapons import weapons
from lang_en import strings
from costs import costs
from ingame_order import ingame_order


# Create the static elements of the home page
def init_page():
	init_characters()
	init_inventory()


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
			for c, val in enumerate([1, 20, 40, 50, 60, 70, 80, 90]):
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
			TD(INPUT(Id=f"use_arti-{char}", type='checkbox', Class='save', checked=True)) +
			TD(BUTTON(strings["add"], Class='arti_list text_button', data_id=f"arti-{char}")) +
			TD(DIV(Id=f"arti-{char}", Class=f'arti_span'))
			,
			data_id=f"check-{char}", Class='unchecked', data_color=characters[char]['element']
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
		for c, val in enumerate([1, 20, 40, 50, 60, 70, 80, 90]):
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
		TD(INPUT(Id=f"use_arti-{char}", type='checkbox', Class='save', checked=True)) +
		TD(BUTTON(strings["add"], Class='arti_list text_button', data_id=f"arti-{char}")) +
		TD(DIV(Id=f"arti-{char}", Class=f'arti_span'))
		,
		data_id=f"check-{char}", Class='unchecked',
	)
	# set up traveler anemo/geo row
	for char, ele in [('traveler_anemo', 'anemo'), ('traveler_geo', 'geo')]:
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
			data_id=f"check-{char}", Class='unchecked', data_color=ele
		)
	doc['character_list'] <= t


def init_inventory():
	# Create a table of items we might need and store their ids in a lookup table
	# char xp, weapon xp, and mora
	t_own = TABLE(Class='borders center')
	t_own <= TR(TH(strings["item"]) + TH(strings["need"]) + TH(strings["have"]) + TH(strings["missing_"]))
	t_own <= TR(TD(IMG(src=f"img/wep_xp_sub_0.png", alt=strings['wep_xp'], title=strings['wep_xp'])) + TD() + TD(INPUT(Type='number', min='0', step="1", value='0', Id='wep_xp_sub_0-user', Class='save')) + TD())
	t_own <= TR(TD(IMG(src=f"img/wep_xp_sub_1.png", alt=strings['wep_xp'], title=strings['wep_xp'])) + TD() + TD(INPUT(Type='number', min='0', step="1", value='0', Id='wep_xp_sub_1-user', Class='save')) + TD())
	t_own <= TR(TD(IMG(src=f"img/wep_xp.png", alt=strings['wep_xp'], title=strings['wep_xp'])) + TD('0', Id='wep_xp-total') + TD(INPUT(Type='number', min='0', step="1", value='0', Id='wep_xp-user', Class='save')) + TD('0', Id='wep_xp-need', Class='good'))
	t_own <= TR(TD(IMG(src=f"img/mora.png", alt=strings['mora'], title=strings['mora'])) + TD('0', Id='mora-total') + TD(INPUT(Type='number', min='0', step="1", value='0', Id='mora-user', Class='save')) + TD('0', Id='mora-need', Class='good'))
	t_own <= TR(TD(IMG(src=f"img/xp.png", alt=strings['xp'], title=strings['xp'])) + TD('0', Id='xp-total') + TD(INPUT(Type='number', min='0', step="1", value='0', Id='xp-user', Class='save')) + TD('0', Id='xp-need', Class='good'))
	t_own <= TR(TD(IMG(src=f"img/xp_sub_1.png", alt=strings['xp'], title=strings['xp'])) + TD() + TD(INPUT(Type='number', min='0', step="1", value='0', Id='xp_sub_1-user', Class='save')) + TD())
	t_own <= TR(TD(IMG(src=f"img/xp_sub_0.png", alt=strings['xp'], title=strings['xp'])) + TD() + TD(INPUT(Type='number', min='0', step="1", value='0', Id='xp_sub_0-user', Class='save')) + TD())
	doc['inven'] <= P(strings['convert_notice']) + t_own

	c = 0
	width = 3
	alt_width = 2
	prev_section = "init"
	t_own = TABLE(Class='borders center spacer')
	t_head = TR()
	for c in range(width):
		t_head <= TH(strings["item"]) + TH(strings["need"]) + TH(strings["have"]) + TH(strings["missing_"])
		if c < width - 1:
			t_head <= TH(Class="spacer")
	t_own <= t_head
	t_row = TR()

	for section, item in ingame_order:
		if section != prev_section:
			if c % width:
				t_own <= t_row
				t_row = TR()
				c = 0
			if prev_section != 'init':
				t_own <= TR(Class='empty_row')
			prev_section = section
		if section in ['element_1', 'common', 'common_rare', 'wam', 'talent']:
			if section in ['element_1', 'wam']:
				if c:
					c = 0
					t_own <= t_row
					t_row = TR()
				t_width = alt_width
			else:
				t_width = width
			prev_section = 'end section'
			for i in range(len(strings[item])-1, -1, -1):
				t_td = TD(IMG(src=f"img/{item}_{i}.png", alt=strings[item][i], title=strings[item][i])) + TD('0', Id=f"{item}_{i}-total") + TD(INPUT(Type='number', min='0', step="1", value='0', Id=f"{item}_{i}-user", Class='save')) + TD('0', Id=f"{item}_{i}-need")
				#t_own <= TR(TD(IMG(src=f"img/{item}_{i}.png", alt=strings[item][i], title=strings[item][i])) + TD('0', Id=f"{item}_{i}-total") + TD(INPUT(Type='number', min='0', step="1", value='0', Id=f"{item}_{i}-user", Class='save')) + TD('0', Id=f"{item}_{i}-need"))
				c += 1
				t_row <= t_td
				if not (c % t_width):
					t_own <= t_row
					t_row = TR()
				elif c % width < width:
					t_row <= TD()
		else:  # section in ['boss', 'element_2', 'local', 'special']:
			t_td = TD(IMG(src=f"img/{item}.png", alt=strings[item], title=strings[item])) + TD('0', Id=f"{item}-total") + TD(INPUT(Type='number', min='0', step="1", value='0', Id=f"{item}-user", Class='save')) + TD('0', Id=f"{item}-need")
			#t_own <= TR(TD(IMG(src=f"img/{item}.png", alt=strings[item], title=strings[item])) + TD('0', Id=f"{item}-total") + TD(INPUT(Type='number', min='0', step="1", value='0', Id=f"{item}-user", Class='save')) + TD('0', Id=f"{item}-need"))
			c += 1
			t_row <= t_td
			if not (c % width):
				t_own <= t_row
				t_row = TR()
			elif c % width < width:
				t_row <= TD()

	if c % width:
		t_own <= t_row

	doc['inven'] <= t_own

	b_char = BUTTON(strings["characters"], Id='button_character', Class='current_tab')
	doc["character"] <= b_char

	b_inven = BUTTON(strings["inventory"], Id="button_inventory")
	doc["inventory"] <= b_inven

	b_reset = BUTTON(strings["reset_all_data"], Id='reset_all')
	doc["reset"] <= b_reset

	b_reset = BUTTON(strings["reset_character"], Id='reset_character')
	doc["reset"] <= b_reset

	b_reset = BUTTON(strings["reset_inventory"], Id='reset_inventory')
	doc["reset"] <= b_reset


init_page()

