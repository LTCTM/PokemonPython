import numpy as np
import pandas as pd
import re


class Database(object):
    def __init__(self):
        # ================读取================
        excel_file = pd.ExcelFile("数据.xlsx")
        self._sheets = {
            "P": pd.read_excel(excel_file, "种族", index_col="ID"),
            "E": pd.read_excel(excel_file, "特性_系_装备", index_col="ID"),
            "S": pd.read_excel(excel_file, "技能", index_col="ID"),
            "特效": pd.read_excel(excel_file, "特效", index_col="Name"),
            "系": pd.read_excel(excel_file, "系", index_col=0, convert_float=True),  # Row
        }
        # ================清洗================
        self._sheets["P"].fillna("", inplace=True)
        self._sheets["S"].fillna("", inplace=True)
        # ================词条================
        self._词条 = {}
        # ========模板========
        template_dict = {
            "Type": "",
            "Power": 0,
            "Rate": 100,
            "Time": 0,
            "Channel": 0,
            "Para": 0,
        }
        # ========解析========
        for ID in np.concatenate((self._sheets["E"].index, self._sheets["S"].index)):
            template_dict.update(
                {"MasterID": ID, "MasterName": self.get_property(ID, "Name")}
            )
            result = []
            if ID[:4] == "E000" and 1 <= int(ID[4:]) <= 18:
                # ====系====
                系名 = template_dict["MasterName"]
                # ==系攻击==
                系攻击 = template_dict.copy()
                系攻击.update({"Type": f"{系名}系攻击", "Power": 150})
                # ==系防御==
                result.append(系攻击)
                防御列 = self._sheets["系"][系名]
                for 防御系 in 防御列.index:
                    value = 防御列[防御系]
                    if value != 100:
                        系防御 = template_dict.copy()
                        if value < 0:
                            系防御.update({"Type": f"{防御系}系无效"})
                        else:
                            系防御.update({"Type": f"{防御系}系防御", "Power": value})
                        result.append(系防御)
            elif ID[0] == "S":
                # ====技能====
                词条 = template_dict.copy()
                all_flags = self.get_property(ID, "Flags").split(" ")
                for flag in all_flags:
                    能力变化 = re.match(r"(STR|DEF|ATS|ADF|SPD)_(UP|DOWN)\((\d)\)", flag)
                    if 能力变化:
                        种类, 升降, 程度 = 能力变化.groups()
                        词条.update({"Type": f"{种类}_{升降}", "Power": 程度})
                        result.append(词条)
            self._词条[ID] = result

    # 入口
    def __call__(self, ID, field=None):
        "和get_property功能相同"
        if field == "Rows":
            return self.get_rows(ID)
        else:
            return self.get_property(ID, field)

    def get_property(self, ID, field=None):
        "返回一个属性的值（文本）或一个字典"
        big_type = ID[0]
        if not re.match(r"[A-Z]\d{5}", ID):
            big_type = "特效"
        if field:
            return self._sheets[big_type].loc[ID, field]
        else:
            return self._sheets[big_type].loc[ID]

    # Rows
    def get_rows(self, ID):
        return self._词条[ID]

    # 特殊属性
    def has_flag(self, ID, *flags):
        "split_symbol参数无法通过位置指定"
        all_flags = self.get_property(ID, "Flags").split(" ")
        return any(flag in all_flags for flag in flags)


# 实体
print("正在加载数据库...")
database = Database()
print("数据库加载成功！")
