from database import database

class Skill(object):
	def __init__(self,parent_game,ID,attacker,channel = 0):
		self._parent_game = parent_game
		self._ID = ID
		self._attacker = attacker
		self.target = "自己" if self.has_flag("自己") else "敌人"
		if self.has_flag("双方","天气","空间"):
			self.target_field = (attacker.master.field,self._parent_game.enemy_of(attacker.master).field)
		else:
			self.target_field = attacker.master.field if self.target == "自己" else self._parent_game.enemy_of(attacker.master).field 
		my_data = database(self._ID)
		self.name = my_data["Name"]
		self.系 = my_data["Xi"]
		self.type = my_data["Type"]
		self.hit_rate = my_data["Hit"] / 100
		self.power = my_data["Power"]
		self.priority = my_data["Priority"]
		self.MP = my_data["MP"]
		self.rows = [row for row in database.get_rows(self._ID) if row["Channel"] == channel]
	def has_flag(self,*flags):
		return database.has_flag(self._ID,*flags)
	@property
	def 是攻击技能(self):
		return self.type != "变化"
	@property
	def brief(self):
		return ""

