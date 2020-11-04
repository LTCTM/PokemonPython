from Database import database
class ManagerEffect(object):
	def __init__(self):
		self._effects = []
	def excute(self,effect):
		effect.on_effect()
		if database(effect.name,"Constant") != "瞬时":
			self._effects.append(effect)
	def remove_all(self,effects):
		for effect in tuple(effects):
			effect.off_grid()
			self._effects.remove(effect)
	def time_pass(self):
		for effect in self._effects:
			effect.time_pass()
			if effect.life_end:
				effect.off_grid()
				self._effects.remove(effect)
	def where(self,**args):
		"可以限制：caster,host,name,constant,is_damage"
		for effect in self._effects:
			for 限制类型,限制值 in args.items():
				if getattr(effect,限制类型) != 限制值:
					break
				yield effect
	def has_effect(self,host,*effect_names):
		"host取None代表不限host"
		for effect_name in effect_names:
			for effect in self.where(host=host):
				if effect.name == effect_name:
					return True
		return False
	def get_effects(self,host,effect_name):
		"host和effect_name可以取None，代表不设限制"
		for effect in self.where(host=host):
			if effect_name is None or effect.name == effect_name:
				yield effect
