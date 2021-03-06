import my_maths
from database import database
from effect import new_effect
from skill import Skill


class Pokemon(object):
    def __init__(self, parent_game, master, xml_node):
        self._parent_game = parent_game
        self.master = master
        # 种族、等级
        self._race = xml_node.find("ID").text
        self.level = int(xml_node.find("Level").text)
        # 名字
        self.name = my_maths.xml_child_text(
            xml_node, "Name", database(self._race, "Name")
        )
        # 觉醒系
        self.觉醒系 = my_maths.xml_child_text(xml_node, "JueXingXi", "一般")
        # 努力值
        self._努力值 = {}
        efos = xml_node.find("EFO")
        for efo in efos:
            self._努力值[efo.tag] = int(efo.text)
        # 个体值
        self.__个体值 = {}
        inds = xml_node.find("IND")
        for ind in inds:
            self.__个体值[ind.tag] = int(ind.text) / 100
        # 装备ID（包含特性和携带物）
        self.equips = {}
        equips = xml_node.find("Equips")
        for equip in equips:
            self.equips[equip.tag] = equip.text
        # 系
        self.equips["Xi1"] = my_maths.xi_ID[self.系[0]]
        self.equips["Xi2"] = my_maths.xi_ID[self.系[1]]
        # 技能ID
        self.skills = []
        skills = xml_node.find("Skills")
        for skill in skills:
            self.skills.append(skill.text)
        # 性格。如果性格节点不存在或者填入非法值，均将被忽略
        self._性格 = {"STR": 1, "DEF": 1, "ATS": 1, "ADF": 1, "SPD": 1}
        p_up_node = xml_node.find("PersonalityUp")
        if p_up_node is not None:
            p_up = p_up_node.text
            if p_up in self._性格:
                self._性格[p_up] = my_maths.PERSONALITY_UP
        p_down_node = xml_node.find("PersonalityDown")
        if p_down_node is not None:
            p_down = p_down_node.text
            if p_down in self._性格:
                self._性格[p_down] = my_maths.PERSONALITY_DOWN
        # 当前状态
        self._never_on_stage = True
        self._dead = False
        self.curHP = self.get_ability("HP")
        self.curMP = self.get_ability("MP")
        # 特殊特征
        self._连续保护 = 0

    def __str__(self):
        return self.name

    # 能力和特征
    @property
    def curHP_rate(self):
        return self.curHP / self.get_ability("HP")

    @property
    def curMP_rate(self):
        return self.curMP / self.get_ability("MP")

    @property
    def 系(self):
        xi1 = database(self._race, "Xi1")
        xi2 = database(self._race, "Xi2")
        return (xi1, xi2)

    def get_ability(self, ability_type, 系=""):
        def rate():
            result = 1
            # 系能力
            if ability_type in ("STR", "ATS"):
                for effect in self.get_effects(系 + "系攻击"):
                    result *= effect.power / 100
            elif ability_type in ("DEF", "ADF"):
                for effect in self.get_effects(系 + "系防御"):
                    result *= effect.power / 100
            # 特性和异常状态的交互，如中毒——毒暴走
            # 能力上升和下降的Effect，如STR_UP
            ability_level = 0
            for effect in self.get_effects(ability_type + "_UP"):
                ability_level += effect.power
            for effect in self.get_effects(ability_type + "_Down"):
                ability_level -= effect.power
            result *= my_maths.ability_rate(ability_type, ability_level)
            return result

        def bonus():
            return 0

        # --------------------
        if ability_type == "HP":
            race = database(self._race, ability_type)
            std = my_maths.HP_std(
                race, self.__个体值[ability_type], self._努力值[ability_type]
            )
            no_equip = my_maths.HP_no_equip(std, self.level)
        elif ability_type == "MP":
            race = 0
            std = my_maths.MP_std()
            no_equip = my_maths.MP_no_equip()
        elif ability_type in ("DEX", "AGL"):
            return rate()
        else:
            race = database(self._race, ability_type)
            std = my_maths.ability_std(
                race, self.__个体值[ability_type], self._努力值[ability_type], 1
            )
            no_equip = my_maths.ability_no_equip(std, self.level)
        return my_maths.ability_real(no_equip, rate(), bonus())

    def get_ability_ref(self, ability_type):
        if ability_type == "HP":
            race = database(self._race, ability_type)
            return my_maths.HP_ref(race, self.level)
        elif ability_type == "MP":
            race = 0
            return my_maths.MP_ref()
        else:
            race = database(self._race, ability_type)
            return my_maths.ability_ref(race, self.level)

    # 状态
    @property
    def dead(self):
        return self._dead

    def 完全防御生效(self):
        rate = 1 / (2 ** self._连续保护)
        success = my_maths.random_in_range(rate)
        if success:
            self._连续保护 += 1
            return True
        else:
            self._连续保护 = 0
            return False

    def 完全防御计数清零(self):
        self._连续保护 = 0

    def get_effects(self, effect_name=None):
        return self._parent_game.manager_effect.get_effects(self, effect_name)

    def has_effect(self, *effect_names):
        return self._parent_game.manager_effect.has_effect(self, *effect_names)

    @property
    def brief(self):
        if self.dead:
            return self.name + " 濒死"
        else:
            can_operate = "行动受限" if self.has_effect("睡眠", "冰冻", "麻痹") else ""
            suffer_dot = "体力不断流失" if self.has_effect("烧伤", "中毒") else ""
            return f"{self.name}  HP:{self.curHP}/{self.get_ability('HP')} MP:{self.curMP} {can_operate} {suffer_dot}"

    def show_detail(self):
        send_message = self._parent_game.send_message
        my_effect_names = tuple(effect.name for effect in self.get_effects())
        # 名字
        系名 = " ".join(name[:-3] for name in my_effect_names if name[-3:] == "系攻击")
        send_message(f"{self.master.name} 的 {self.name}： {系名}")
        # HP、MP条
        if self._parent_game.local_game:
            BAR_LEN = 24
            # =
            HP_bar = "■" * int(self.curHP_rate * BAR_LEN) + "—" * (
                BAR_LEN - int(self.curHP_rate * BAR_LEN)
            )
            HP_bar = "\033[1;32;40m" + HP_bar + "\033[0m"  # 改颜色
            HP_str = f"HP: {HP_bar} {self.curHP}/{self.get_ability('HP')}"
            # =
            MP_bar = "■" * int(self.curMP_rate * BAR_LEN) + "—" * (
                BAR_LEN - int(self.curMP_rate * BAR_LEN)
            )
            MP_bar = "\033[1;34;40m" + MP_bar + "\033[0m"  # 改颜色
            MP_str = f"MP: {MP_bar} {self.curMP}/{self.get_ability('MP')}"
            print(HP_str)
            print(MP_str)
        else:
            send_message(
                f"#AP|HP|{self.curHP}|{self.get_ability('HP')}|{self.curHP_rate}"
            )
            send_message(
                f"#AP|MP|{self.curMP}|{self.get_ability('MP')}|{self.curMP_rate}"
            )
        # effect
        effect_names = {
            name for name in my_effect_names if not name[-3:] in ("系防御", "系攻击", "系无效")
        }
        send_message(f"状态：{' '.join(effect_names)}\n")

    @property
    def can_operate(self):
        if self.has_effect("麻痹"):
            if my_maths.random_in_range(0.25):
                return False
        if self.dead:
            return False
        return not self.has_effect("睡眠", "冰冻", "害怕")

    def suffer_dot(self):
        pass

    # 动作
    def suffer_damage(self, damage):
        return self.lose_HP(damage)

    def lose_HP(self, amount):
        begining_HP = self.curHP
        if self.curHP > amount:
            self.curHP -= amount
        else:
            self.curHP = 0
            self.die()
        return begining_HP - self.curHP

    def die(self):
        if not self.dead:
            self._dead = True
            self.curHP = 0
            self._parent_game.manager_effect.remove_all(self.get_effects())
            self._parent_game.send_message(self.name + "倒下了！")

    def choose_skill(self, allow_cancel=True):
        valid = False
        chosen_index = ""
        while not valid:
            text = "请选择技能：\n" + ("c:取消\n" if allow_cancel else "")
            # 依次输出每个技能的名称
            text += "\n".join(
                f"{i} {database(skill,'Name')}" for i, skill in enumerate(self.skills)
            )
            self._parent_game.send_message(text, self.master, True)
            chosen_index = self._parent_game.receive_message(self.master)
            if allow_cancel and chosen_index == "c":
                valid = True
            elif chosen_index.isdigit():
                chosen_index = int(chosen_index)
                if self.curMP < database(self.skills[chosen_index], "MP"):
                    self._parent_game.send_message("蓝不够！", self)
                else:
                    valid = True
            else:
                self._parent_game.send_message("请正确输入数字！", self)
        return chosen_index

    def go_off_stage(self):
        useless_effects = self._parent_game.manager_effect.where(
            host=self, constant="临时"
        )
        self._parent_game.manager_effect.remove_all(useless_effects)

    def go_on_stage(self):
        active_equip_IDs = filter(
            lambda equip_ID: database(equip_ID, "Opportunity") == "每次"
            or self._never_on_stage,
            self.equips.values(),
        )
        for equip_ID in active_equip_IDs:
            for equip_row in database.get_rows(equip_ID):
                effect = new_effect(equip_row, self._parent_game, None, self)
                self._parent_game.manager_effect.excute(effect)
        self._never_on_stage = False

    def use_skill(self, index):
        skill_ID = self.skills[index]
        if database(skill_ID, "Name") == "诅咒":
            if "幽灵" in self.系:
                channel = 0
            else:
                channel = 1
        else:
            channel = 0
            self._parent_game.enemy_of(self)
        skill = Skill(self._parent_game, skill_ID, self, channel)
        self._parent_game.send_skill(self, skill)

