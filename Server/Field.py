class Field(object):
	def __init__(self,parent_game,master):
		self._parent_game=parent_game
		self._master=master
	#def get_effects(self,effect_name):
		#return self._parent_game.manager_effect.get_effects(self,effect_name)
	def has_effect(self,effect_name):
		return self._parent_game.manager_effect.has_effect(self,effect_name)
	@property
	def pokemon_on(self):
		return self._master.pokemon_on_stage



