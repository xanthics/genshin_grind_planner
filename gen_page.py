from browser import document as doc
from browser.html import TABLE, TR, TH, TD, INPUT, SELECT, OPTION, DIV, BUTTON, SPAN, LI, H2, H3, IMG, COLGROUP, COL

from characters import characters
from weapons import weapons
from lang_en import strings
from costs import costs


# Create the static elements of the home page
def init_page():
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
		COL(Class='left_dotted')
	)
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
		TH("Click to remove", colspan=2)
	)
	for char in sorted(characters):
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
			TD(BUTTON("Add", Class='arti_list text_button', data_id=f"arti-{char}")) +
			TD(DIV(Id=f"arti-{char}", Class=f'arti_span'))
			,
			data_id=f"check-{char}", Class='unchecked', data_color=characters[char]['element']
		)

	doc['test'] <= t
	# In game order is inconsistent manual list to override
	ingame_order = [
		('common', 'slime'),
		('common', 'mask'),
		('common', 'scroll'),
		('common', 'arrowhead'),
		('common_rare', 'horn'),
		('common_rare', 'ley_line'),
		('common_rare', 'chaos'),
		('common_rare', 'mist'),
		('common_rare', 'sacrificial_knife'),
		('common', 'f_insignia'),
		('common', 'th_insignia'),
		('boss', 'tusk_of_monoceros_caeli'),
		('boss', 'shard_of_a_foul_legacy'),
		('boss', 'shadow_of_the_warrior'),
		('boss', 'dvalins_claw'),
		('boss', 'dvalins_plume'),
		('boss', 'dvalins_sigh'),
		('boss', 'ring_of_boreas'),
		('boss', 'spirit_locket_of_boreas'),
		('boss', 'tail_of_boreas'),
		('element_2', 'hurricane_seed'),
		('element_2', 'lightning_prism'),
		('element_2', 'basalt_pillar'),
		('element_2', 'hoarfrost_core'),
		('element_2', 'everflame_seed'),
		('element_2', 'cleansing_heart'),
		('common', 'nectar'),
		('element_1', 'brilliant_diamond'),
		('common_rare', 'bone_shard'),
		('element_1', 'agnidus_agate'),
		('element_1', 'varunada_lazurite'),
		('element_1', 'vajrada_amethyst'),
		('element_1', 'vayuda_turqoise'),
		('element_1', 'shivada_jade'),
		('element_1', 'prithiva_topaz'),
		('talent', 'freedom'),
		('talent', 'resistance'),
		('talent', 'ballad'),
		('talent', 'prosperity'),
		('talent', 'diligence'),
		('talent', 'gold'),
		('wam', 'decarabian'),
		('wam', 'boreal_wolf'),
		('wam', 'dandelion_gladiator'),
		('wam', 'guyun'),
		('wam', 'mist_veiled_elixer'),
		('wam', 'aerosiderite'),
		('local', 'calla_lily'),
		('local', 'wolfhook'),
		('local', 'valberry'),
		('local', 'cecilia'),
		('local', 'windwheel_aster'),
		('local', 'philanemo_mushroom'),
		('local', 'jueyun_chili'),
		('local', 'noctilucous_jade'),
		('local', 'silk_flower'),
		('local', 'glaze_lilly'),
		('local', 'starconch'),
		('local', 'violetgrass'),
		('local', 'small_lamp_grass'),
		('local', 'dandelion_seed'),
		('local', 'cor_lapis')
	]

	# Create a table of items we might need and store their ids in a lookup table
	# char xp, weapon xp, and mora
	t_own = TABLE(Class='borders')
	t_own <= TR(TH("Item") + TH("Need") + TH("Have") + TH("Missing"))
	t_own <= TR(TD(IMG(src=f"img/xp.png", alt=strings['xp'], title=strings['xp'])) + TD('0', Id='xp-total') + TD(INPUT(Type='number', min='0', step="1", value='0', Id='xp-user', Class='save')) + TD('0', Id='xp-need', Class='good'))
	t_own <= TR(TD(IMG(src=f"img/wep_xp.png", alt=strings['wep_xp'], title=strings['wep_xp'])) + TD('0', Id='wep_xp-total') + TD(INPUT(Type='number', min='0', step="1", value='0', Id='wep_xp-user', Class='save')) + TD('0', Id='wep_xp-need', Class='good'))
	t_own <= TR(TD(IMG(src=f"img/mora.png", alt=strings['mora'], title=strings['mora'])) + TD('0', Id='mora-total') + TD(INPUT(Type='number', min='0', step="1", value='0', Id='mora-user', Class='save')) + TD('0', Id='mora-need', Class='good'))
	for section, item in ingame_order:
		if section in ['boss', 'element_2', 'local']:
			t_own <= TR(TD(IMG(src=f"img/{item}.png", alt=strings[item], title=strings[item])) + TD('0', Id=f"{item}-total") + TD(INPUT(Type='number', min='0', step="1", value='0', Id=f"{item}-user", Class='save')) + TD('0', Id=f"{item}-need", Class='good'))
		if section in ['element_1', 'common', 'common_rare', 'wam', 'talent']:
			for i in range(len(strings[item])-1, -1, -1):
				t_own <= TR(TD(IMG(src=f"img/{item}_{i}.png", alt=strings[item][i], title=strings[item][i])) + TD('0', Id=f"{item}_{i}-total") + TD(INPUT(Type='number', min='0', step="1", value='0', Id=f"{item}_{i}-user", Class='save')) + TD('0', Id=f"{item}_{i}-need", Class='good'))

	doc['inven'] <= t_own

	b_char = BUTTON("Characters", Id='button_character', Class='current_tab')
	doc["character"] <= b_char

	b_inven = BUTTON("Inventory", Id="button_inventory")
	doc["inventory"] <= b_inven

	b_reset = BUTTON("Reset All Data", Id='reset_all')
	doc["reset"] <= b_reset

	b_reset = BUTTON("Reset Character", Id='reset_character')
	doc["reset"] <= b_reset

	b_reset = BUTTON("Reset Inventory", Id='reset_inventory')
	doc["reset"] <= b_reset

init_page()

