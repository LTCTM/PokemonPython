import xml.etree.ElementTree as ET
from Pokemon import Pokemon
from Field import Field

class Player(object):
	def __init__(self,parent_game,name,save_file):
		self.name = name
		self._parent_game = parent_game
		#读取存档，建立Pokemon
		xmlRoot = ET.parse(save_file).getroot()
		self._pokemons = []
		for pokemon_node in xmlRoot:
			self._pokemons.append(Pokemon(parent_game,self,pokemon_node))
		self.pokemon_on_stage = None
		#建立场地
		self.field = Field(parent_game,self)
	#状态
	def lose(self):
		return len([pokemon for pokemon in self._pokemons if not pokemon.dead]) == 0
	#宝可梦
	def choose_pokemon(self,allow_cancel = True):
		valid = False
		while not valid:
			text = f"请{self.name}选择宝可梦：\n" + 'c:取消\n' if allow_cancel else ''
			#依次输出每个宝可梦的简略信息
			for i in range(0,len(self._pokemons)):
				text+="%d %s\n" % (i,self._pokemons[i].brief)
			#[:-1]为了去掉最后一个回车
			self._parent_game.send_message(text[:-1],self,True)
			chosen_index = self._parent_game.receive_message(self)
			if allow_cancel and chosen_index == "c":
				break
			chosen_index = int(chosen_index)
			if self._pokemons[chosen_index].dead :
				self._parent_game.send_message("宝可梦处于濒死状态！",self)
			else:
				valid = True
		return chosen_index

	def select_pokemon(self,index):
		old_pokemon = self.pokemon_on_stage
		self.pokemon_on_stage = self._pokemons[index]
		#旧怪去除临时状态
		if old_pokemon is not None:
			old_pokemon.go_off_stage()
		#新怪加上装备状态
		self.pokemon_on_stage.go_on_stage()
		#提示
		self._parent_game.send_message(self.name + "说：就决定是你了！" + self.pokemon_on_stage.name + "！",want_response=False)
	#指令
	def choose_command(self):
		try:
			chosen_command = None
			while chosen_command == None or chosen_command == "c":
				self._parent_game.send_message(f"请{self.name}选择指令\n0:打\n1:兽",self,True)
				打_兽 = self._parent_game.receive_message(self)
				if 打_兽 == "1":
					chosen_command = self.choose_pokemon()
				else:
					chosen_command = self.pokemon_on_stage.choose_skill()
			return {"打_兽":打_兽,"index":chosen_command}
		except ConnectionError:
			return "客户端掉线"
	def excute_command(self,command):
		if command["打_兽"] == "1":
			self.select_pokemon(command["index"])
		else:
			self.pokemon_on_stage.use_skill(command["index"])
