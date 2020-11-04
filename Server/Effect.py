import MyMaths
import sys
def new_effect(row,parent_game,caster,host,skill=None):
	try:
		effect_class = getattr(sys.modules["Effect"],row['Type'] + "特效")
		return effect_class(row,parent_game,caster,host,skill)
	except:
		return 基本特效(row,parent_game,caster,host,skill)

class 基本特效(object):
	def __init__(self,row,parent_game,caster,host,skill):
		self.name = row["Type"]
		self.power = row["Power"]
		self.channel = row["Channel"]
		self.para = row["Para"]
		self.__remaining_time = row["Time"]
		self._parent_game = parent_game
		self.caster = caster
		self.host = host
		self.skill = skill
		self.__life_end = False
	@property
	def life_end(self):
		return self.__life_end
	def time_pass(self):
		if self.__remaining_time > 1:
			self.__remaining_time-=1
		elif self.__remaining_time == 1:
			self.__life_end = True
	def __repr__(self):
		return self.name
	def on_effect(self):
		pass
	def off_grid(self):
		pass

class 伤害特效(基本特效):
	def on_effect(self):
		if self.skill.type == "物理":
			att_ability = self.caster.get_ability("STR",self.skill.系)
			def_ability = self.host.get_ability("DEF",self.skill.系)
		elif self.skill.type == "魔法":
			att_ability = self.caster.get_ability("ATS",self.skill.系)
			def_ability = self.host.get_ability("ADF",self.skill.系)
		elif self.skill.type == "震荡":
			att_ability = self.caster.get_ability("STR",self.skill.系)
			def_ability = self.host.get_ability("ADF",self.skill.系)
		elif self.skill.type == "化形":
			att_ability = self.caster.get_ability("ATS",self.skill.系)
			def_ability = self.host.get_ability("DEF",self.skill.系)
		#damage=MyMaths.damage(att_ability,def_ability,self.power)
		damage = 99999999999999
		damage = self.host.suffer_damage(damage)
		self._parent_game.send_message("%s对%s造成了%d伤害！" % (self.caster.name,self.host.name,damage))

