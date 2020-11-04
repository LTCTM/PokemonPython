import random
#简化
def xml_child_text(parent_node,child_name,default_value):
	child_node = parent_node.find(child_name)
	if child_node is None:
		return default_value
	else:
		return child_node.text
def random_True_False():
	return random.choice((True,False))
def random_in_range(rate):
	return rate >= random.random()
def random_damage(damage):
	rate = None
	while rate == None or rate > 3 or rate < -3:
		rate = random.normalvariate(0,1)
	rate/=20
	return (1 + rate) * damage

#获得值
LEVEL_MAX = 100
MP = 960
PERSONALITY_UP = 1.1
PERSONALITY_DOWN = 0.9

xi_ID = {"无":"E00000","一般":"E00001","格斗":"E00002","飞行":"E00003","毒":"E00004",
		"地面":"E00005","岩石":"E00006","虫":"E00007","幽灵":"E00008","钢":"E00009",
		"火":"E00010","水":"E00011","草":"E00012", "电":"E00013","超能力":"E00014",
		"冰":"E00015","龙":"E00016","恶":"E00017","妖精":"E00018",
		"":"E00000"}
#公式计算
def ability_std(种族值, 个体值, 努力值, 性格值):
	return (种族值 * 2 * (1 + 个体值) + 努力值) * 性格值
def HP_std(种族值, 个体值, 努力值):
	return 种族值 * 2 * (1 + 个体值) + 努力值
def MP_std():
	return MP
	
def ability_no_equip(标准等级值, 等级):
	return 标准等级值 * (0.05 + 等级 / LEVEL_MAX) * 5
def HP_no_equip(标准等级值, 等级):
	return round(标准等级值 * (4 + 等级 / LEVEL_MAX) / 2) * 48
def MP_no_equip():
	return MP

def ability_ref(种族值, 等级):
	aa = ability_std(种族值,0,0,0)
	return ability_no_equip(aa, 等级)
def HP_ref(种族值, 等级):
	aa = HP_std(种族值,0,0)
	return HP_no_equip(aa, 等级)
def MP_ref():
	return MP

def ability_real(裸装值,倍率,固定值):
	return 裸装值 * 倍率 + 固定值

def ability_rate(ability_type,ability_level):
	普通能力 = {"STR","DEF","ATS","ADF","SPD"}
	命中回避 = {"DEX","AGL"}
	if ability_level == 0:
		return 1
	elif ability_level > 6:
		ability_level = 6
	elif ability_level < -6:
		ability_level = -6

	if ability_type in 普通能力:
		if ability_level > 0:
			return (2 + ability_level) / 2
		else:
			return 2 / (2 + ability_level)
	elif ability_type in 命中回避:
		if ability_level > 0:
			return (3 + ability_level) / 3
		else:
			return 3 / (3 + ability_level)
	else:
		raise KeyError("能力类型不存在！")

def damage(att_ability,def_ability,power):
	return att_ability / def_ability * power * 48