from browser import document as doc
from browser import html, window, bind
from browser.html import TABLE, TR, TH, TD, INPUT, SELECT, OPTION, DIV, BUTTON, SPAN
from browser.local_storage import storage

from characters import characters
from weapons import weapons
from artifacts import artifacts
from lang_en import strings
from costs import costs


storage_key = "genshin_grind_planner"


# Setter storage so that we can differentiate values on this site from others at the same domain
def set_storage(key, val):
	storage["{}-{}".format(storage_key, key)] = val


# Getter for storage so that we can differentiate values on this site from others at the same domain
def get_storage(key):
	return storage["{}-{}".format(storage_key, key)]


# deleter for storage so that we can differentiate values on this site from others at the same domain
def del_storage(key):
	nkey = "{}-{}".format(storage_key, key)
	if nkey in storage.keys():
		del storage[nkey]


# Check if a value exists in storage
def check_storage(key):
	return "{}-{}".format(storage_key, key) in storage


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
	# TODO: element ids
	for char in characters:
		# set up level select
		lvlc = SELECT(Id=f"level_current_{char}", Class=f"{char} save")
		lvlt = SELECT(Id=f"level_goal_{char}", Class=f"{char} save")
		for lvl in [lvlc, lvlt]:
			for val in [1, 20, 40, 50, 60, 70, 80, 90]:
				lvl <= OPTION(f"{val}")
		# Set up talent select
		t1c = SELECT(Id=f"talent_1_c_{char}", Class=f"{char} save")
		t1t = SELECT(Id=f"talent_1_t_{char}", Class=f"{char} save")
		t2c = SELECT(Id=f"talent_2_c_{char}", Class=f"{char} save")
		t2t = SELECT(Id=f"talent_2_t_{char}", Class=f"{char} save")
		t3c = SELECT(Id=f"talent_3_c_{char}", Class=f"{char} save")
		t3t = SELECT(Id=f"talent_3_t_{char}", Class=f"{char} save")
		for st in [t1t, t1c, t2t, t2c, t3t, t3c]:
			for cost in costs['talent']:
				st <= OPTION(cost)
		# Set up weapon select
		ws = SELECT(Id=f"weapon_{char}", data_id=f"select_{char}", Class=f'weapon {char} save')
		ws <= OPTION('--')
		sort_dict_wep = {}
		for item in weapons[characters[char]['weapon']]:
			if weapons[characters[char]['weapon']][item]['wam'] != 'unk':
				sort_dict_wep[strings[characters[char]['weapon']][item]] = item
		for k in sorted(sort_dict_wep):
			ws <= OPTION(k, value=sort_dict_wep[k])
		wlvlc = SELECT(Id=f"weapon_c_{char}", Class=f"{char} save")
		wlvlt = SELECT(Id=f"weapon_t_{char}", Class=f"{char} save")
		for lvl in [wlvlc, wlvlt]:
			for val in [1, 20, 40, 50, 60, 70, 80, 90]:
				lvl <= OPTION(f"{val}")
		# Create table row for character
		t <= TR(
			TD(INPUT(Id=f"check_{char}", type='checkbox', data_id=f"check_{char}", Class='char_select save')) +
			TD(char) +
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
			TD(BUTTON("Add", Class='arti_list text_button', data_id=f"arti_{char}")) +
			TD(DIV(Id=f"arti_{char}", Class=f'arti_span {char}'))
			,
			data_id=f"check_{char}", Class='unchecked'
		)

	doc['main'] <= html.DIV(Id="test")
	doc['test'] <= t

	for k, v in list_storage():
		if v == 'checked':
			doc[k].checked = True
			for elt in doc.get(selector='TR[data-id="{}"]'.format(k)):
				elt.attrs['class'] = 'checked'
		elif 'select' in v:
			doc[k].value = v.split('-')[1]
		elif v == 'y':
			target, ev_id = k.split('-')
			b = BUTTON(strings['artifacts'][ev_id], Class='text_button saved_arti', Id=f"{target}-{ev_id}", data_arti=ev_id)
			b.bind('click', delete_me)
			doc[target] <= b
		else:
			print(f"Invalid stored data: {k}, {v}")

	# Function for saving changes
	@bind('.save', 'change')
	def save_state(ev):
		if ev.target.type == 'checkbox':
			if ev.target.checked:
				set_storage(ev.target.id, 'checked')
			else:
				del_storage(ev.target.id)
		elif ev.target.type == 'select-one':
			if ev.target.selectedIndex:
				set_storage(ev.target.id, f"select-{ev.target.value}")
			else:
				del_storage(ev.target.id)
		else:
			print(f"Unhandled element type for storage: {ev.target.type}")

	# Function for fading rows
	@bind('.char_select', 'click')
	def togglerow(ev):
		binstate = ev.target.checked
		newstate = 'checked' if binstate else 'unchecked'
		for elt in doc.get(selector='TR[data-id="{}"]'.format(ev.target.attrs['data-id'])):
			elt.attrs['class'] = newstate

	# Function for showing a list of artifacts on click
	@bind('.arti_list', 'click')
	def showartis(ev):
		if 'vertical-menu' in doc:
			del doc['vertical-menu']
		doc.unbind('mouseclick', custom_menu)

		ev.stopPropagation()
		print("hi")
		# Set up artifact select
		arti = DIV(Id='vertical-menu', Class='vertical-menu')
		for art in artifacts:
			temp = DIV(strings['artifacts'][art], Id=art, data_id=ev.target.attrs["data-id"], Class='vertical-menu menu-item')
			temp.bind('click', custom_menu)
			arti <= temp
		arti.top = ev.y
		arti.left = ev.x
		doc <= arti
		doc.bind('click', custom_menu)


# Function to handle deleting artifacts
def delete_me(ev):
	del_storage(ev.target.id)
	del doc[ev.target.id]


# Handle mouse clicks when the custom menu is present
def custom_menu(ev):
	if 'data-id' in ev.target.attrs and 'menu-item' in ev.target.attrs['class'] and 'vertical-menu' in ev.target.attrs['class']:
		if f"{ev.target.attrs['data-id']}-{ev.target.id}" not in doc:
			b = BUTTON(strings['artifacts'][ev.target.id], Class='text_button saved_arti', Id=f"{ev.target.attrs['data-id']}-{ev.target.id}", data_arti=ev.target.id)
			b.bind('click', delete_me)
			doc[ev.target.attrs["data-id"]] <= b
			set_storage(f"{ev.target.attrs['data-id']}-{ev.target.id}", 'y')
		ev.stopPropagation()
	else:
		if 'vertical-menu' in doc:
			del doc['vertical-menu']
		doc.unbind('mouseclick', custom_menu)


b_reset = html.BUTTON("Reset Data")
b_reset.bind("click", reset_data)
doc["reset"] <= b_reset
init_page()
del doc['loading']

