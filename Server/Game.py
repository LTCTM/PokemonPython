import os
import xml.etree.ElementTree as ET
import my_maths
from web import GameConnection
from task import Task
from effect import new_effect
from managerEffect import ManagerEffect
from pokemon import Pokemon
from player import Player
from database import database

class Game(object):
	#==========状态和属性==========
	def __init__(self):
		#创建Manager
		self.manager_effect = ManagerEffect()
		#加载Setting，创建Player
		setting_node = ET.parse("Setting.xml").getroot()
		self.local_game = False if my_maths.xml_child_text(setting_node,"LocalGame",True) == "False" else True
		if not self.local_game:
			self._connection = GameConnection()
			self._player_names = self._connection.player_names
			self._player_files = self._connection.player_files
		else:
			self._player_names = ("Blue","Red")
			self._player_files = {"Blue":"t1.xml","Red":"t2.xml"}
		self.players = (Player(self,self._player_names[0],self._player_files[self._player_names[0]]),
						Player(self,self._player_names[1],self._player_files[self._player_names[1]]))
	def enemy_of(self,player):
		return self.players[1] if player == self.players[0] else self.players[0]

	#==========行为==========
	#游戏开始
	def begin(self):
		self.cls()
		self.send_message("游戏开始！")
		#两边都出第一只怪
		for player in self.players:
			player.select_pokemon(0)
		#循环指令-执行
		result = "游戏继续"
		while result == "游戏继续":
			self.cls()
			self.players[0].pokemon_on_stage.show_detail()
			self.players[1].pokemon_on_stage.show_detail()
			commands = self.choose_command()
			if "客户端掉线" in commands.values():
				raise ConnectionError()
			self.excute_command(commands)
			result = self.turn_end()
			self.turn_end_pause()
		self.cls()
		self.send_message("游戏结束！" + result)
		self.game_over()
	#指令
	def choose_command(self):
		commands = {}
		if self.local_game:
			for player in self.players:
				commands[player] = player.choose_command()
		else:
			task1 = Task.start_new(self.players[0].choose_command)
			task2 = Task.start_new(self.players[1].choose_command)
			commands[self.players[0]] = task1.result
			commands[self.players[1]] = task2.result
		return commands
	def excute_command(self,commands):
		player1 = self.players[0]
		player2 = self.players[1]
		#得到大家选了“打”还是“兽”
		打_兽_commands = {player:command["打_兽"] for player,command in commands.items()}
		if 打_兽_commands[player1] == "1":
			#第一个玩家选了“兽”
			player1.excute_command(commands[player1])
			player2.excute_command(commands[player2])
		elif 打_兽_commands[player2] == "1":
			#第二个玩家选了“兽”
			player2.excute_command(commands[player2])
			player1.excute_command(commands[player1])
		else:
			#大家都选择“打”
			pokemon1 = player1.pokemon_on_stage
			pokemon2 = player2.pokemon_on_stage
			pokemon1_priority = database(pokemon1.skills[commands[player1]["index"]],"Priority")
			pokemon2_priority = database(pokemon1.skills[commands[player2]["index"]],"Priority")
			if pokemon1_priority > pokemon2_priority:
				player1.excute_command(commands[player1])
				player2.excute_command(commands[player2])
			elif pokemon1_priority < pokemon2_priority:
				player2.excute_command(commands[player2])
				player1.excute_command(commands[player1])
			else:
				pokemon1_SPD = pokemon1.get_ability('SPD')
				pokemon2_SPD = pokemon2.get_ability('SPD')
				if pokemon1_SPD > pokemon2_SPD:
					player1.excute_command(commands[player1])
					player2.excute_command(commands[player2])
				elif pokemon1_SPD < pokemon2_SPD:
					player2.excute_command(commands[player2])
					player1.excute_command(commands[player1])
				else:
					if my_maths.random_True_False():
						player1.excute_command(commands[player1])
						player2.excute_command(commands[player2])
					else:
						player2.excute_command(commands[player2])
						player1.excute_command(commands[player1])
	#把技能从攻击方发送到目标场地
	def send_skill(self,attacker,skill):
		"技能能否成功发动。不能动的情况包括蓝不足、睡眠冰冻麻痹等"
		def can_release():
			if attacker.curMP < skill.MP:
				self.send_message(attacker.name + "的能量不够！")
				return False
			if not attacker.can_operate:
				return False
			if skill.name == "腹大鼓":
				if attacker.curHP_rate <= 0.5:
					self.send_message(attacker.name + "的体力不够！")
					return False
			elif (skill.name == "诅咒" and "幽灵" in attacker.系) or skill.name == "替身":
				if attacker.curHP_rate <= 0.25:
					self.send_message(attacker.name + "的体力不够！")
					return False
			if skill.has_flag("天气"):
				if self.manager_effect.has_effect(None,"天气锁"):
					self.send_message("场上存在天气锁，无法发动天气技能！")
					return False
			return True
		#变系
		def change_系():
			if skill.name == "觉醒力量":
				skill.系 = attacker.觉醒系
				self.send_message("觉醒力量为" + skill.系 + "系！")
			elif attacker.has_effect("一般皮肤"):
				skill.系 = "一般"
			return skill.系
		#判命中
		def judge_hit(target_field,target_pokemon):
			if skill.has_flag("自己","场地","双方","天气","空间"):
				return True
			if skill.has_flag("必中"):
				return False
			if target_field.has_effect("雨天") and skill.has_flag("雨天必中"):
				return True
			if skill.has_flag("一击必杀"):
				hit_rate = skill.hit_rate + (attacker.level - target_pokemon.level) / 100
			else:
				hit_rate = skill.hit_rate * attacker.get_ability("DEX")
			if target_field.has_effect("沙尘暴"):
				hit_rate*=0.7

			if my_maths.random_in_range(hit_rate):
				return True
			else:
				self.send_message(attacker.name + "的攻击没有命中！")
				return False
		#技能是否有效果，比如电打地面，毒打钢
		def has_effect(target_field,target_pokemon):
			if target_pokemon.has_effect("完全防御") or (target_pokemon.has_effect("王者盾牌") and skill.是攻击技能):
				if target_pokemon.完全防御生效():
					self.send_message(target_pokemon.name + "防住了攻击！")
					return False
				else:
					self.send_message(target_pokemon.name + "的防御失败了！")
				#完全防御效果=self.manager_effect.where(name="完全防御")+self.manager_effect.where(name="王者盾牌")
				#self.manager_effect.remove_all(完全防御效果)
			else:
				target_pokemon.完全防御计数清零()
			if target_pokemon.has_effect(skill.系 + "系无效") or ("草" in target_pokemon.系 and skill.name == "寄生种子") or ("冰" in target_pokemon.系 and skill.name == "绝对零度"):
				self.send_message("对%s似乎没什么效果……" % (target_pokemon.name,))
				return False
			return True
		#开始
		if can_release():
			attacker.curMP-=skill.MP #耗蓝
			change_系()
			if skill.has_flag("双方","天气","空间"):
				for t_field in skill.target_field:
					t_pokemon = t_field.pokemon_on
					if judge_hit(t_field,t_pokemon):
						if has_effect(t_field,t_pokemon):
							self.excute_skill(attacker,t_field,skill)
			else:
				t_field = skill.target_field
				t_pokemon = t_field.pokemon_on
				if judge_hit(t_field,t_pokemon):
					if has_effect(t_field,t_pokemon):
						self.excute_skill(attacker,t_field,skill)
				
	#技能特效分类投递至Field和Pokemon并依次生效
	def excute_skill(self,attacker,target_field,skill):
		target_pokemon = target_field.pokemon_on
		#根据环境把所有词条的值改成最终值
		def change_row(row):
			effect_type = database(row["Type"])
			if effect_type["IsDamage"] == "TRUE":
				if attacker.has_effect("铁拳") and skill.has_flag("拳"):
					row["power"]*=1.2
				if target_field.has_effect("雨天"):
					if skill.系 == "火":
						row["power"]*=2
					elif skill.系 == "水":
						row["power"]/=2
			if skill.has_flag("天气"):
				if attacker.has_effect(skill.name + "延长"):
					row["Time"]+=3
			return row
		#判断特效能否生效，若能，再判几率。全部成功那么加进组
		def judge_row(row):
			#判几率
			rate = row["Rate"]
			if attacker.has_effect("天恩"):
				rate*=2
			if not my_maths.random_in_range(rate):
				return False

			if "毒" in target_pokemon.系 and row["Type"] == "中毒":
				return False
			if "火" in target_pokemon.系 and row["Type"] == "烧伤":
				return False
			if "冰" in target_pokemon.系 and row["Type"] == "冰冻":
				return False
			if attacker.has_effect("全力攻击") and (not skill.type in ("变化","")) and (not database(row["Type"],"IsDamage") == "TRUE"):
				return False
			return True
		#生成Effect
		effects = []
		for row in skill.rows:
			if judge_row(row):
				change_row(row)
				effect_type = database(row["Type"])
				effects.append(new_effect(row,self,attacker,target_field if effect_type["Target"] == "Field" else target_pokemon,skill))
		#先对场地的每个特效依次触发OnEffect，之后把持续性特效放进EffectManager
		field_effects = [effect for effect in effects if database(effect.name,"Target") == "Field"]
		for effect in field_effects:
			self.manager_effect.excute(effect)
		#对Pokemon先依次执行OnEffect直至其死亡，死亡后的Effect不发动
		#对于那些已发动OnEffect的特效，把他们挂进EffectManager
		pokemon_effects = [effect for effect in effects if database(effect.name,"Target") == "Pokemon"]
		for effect in pokemon_effects:
			self.manager_effect.excute(effect)
	def turn_end(self):
		#结算dot伤害
		for player in self.players:
			player.pokemon_on_stage.suffer_dot()
		#判断游戏是否结束
		if self.players[0].lose():
			if self.players[1].lose():
				return "平局。"
			else:
				return self.players[1].name + "胜利！"
		elif self.players[1].lose():
			return self.players[0].name + "胜利！"
		#若没有结束，出现精灵死亡则需换新精灵上场
		for player in self.players:
			if player.pokemon_on_stage.dead:
				index = player.choose_pokemon(False)
				player.select_pokemon(index)
		self.manager_effect.time_pass()
		return "游戏继续"
	#==========收发消息==========
	def cls(self,target:Player="Both"):
		if self.local_game:
			os.system('cls')
		else:
			if target == "Both":
				self._connection.send_message("#Clear",self._player_names,False) 
			else:
				self._connection.send_message("#Clear",(target.name,),False)
	def turn_end_pause(self):
		if self.local_game:
			os.system('pause')
		else:
			self._connection.send_message("#TurnEnd",self._player_names,False) 
	def game_over(self):
		if not self.local_game:
			self._connection.send_message("#GameOver",self._player_names,False) 
	def send_message(self,message,target:Player="Both",want_response:bool=False):
		if self.local_game:
			print(message)
		else:
			if target == "Both":
				self._connection.send_message(message,self._player_names,want_response) 
			else:
				self._connection.send_message(message,(target.name,),want_response)
	def receive_message(self,target:Player):
		if self.local_game:
			return input("")
		else:
			return self._connection.receive_message(target.name)
