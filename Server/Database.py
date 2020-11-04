import pandas as pd
import re

class Database(object):
	def __init__(self):
		excel_file = pd.ExcelFile("数据.xlsx")
		self._files = {
			"P":pd.read_excel(excel_file,"种族",index_col="ID"),
			"E":pd.read_excel(excel_file,"特性_系_装备",index_col="ID"),
			"S":pd.read_excel(excel_file,"技能",index_col="ID"),
			"特效":pd.read_excel(excel_file,"特效",index_col="Name"),
			"词条":pd.read_excel(excel_file,"词条",index_col="MasterID") #Row
			   }
		self._files["P"].fillna("",inplace=True)
		self._files["S"].fillna("",inplace=True)
	#入口
	def __call__(self,ID,field = None):
		"和get_property功能相同"
		if field == "Rows":
			return self.get_rows(ID)
		else:
			return self.get_property(ID,field)
	def get_property(self,ID,field = None):
		"返回一个属性的值（文本）或一个字典"
		big_type = ID[0]
		if not re.match(r"[A-Z]\d{5}",ID):
			big_type = "特效"
		if field:
			return self._files[big_type].loc[ID,field]
		else:
			return self._files[big_type].loc[ID]
	#Rows
	def get_rows(self,ID):
		sheet=self._files["词条"].loc[ID]
		if isinstance(sheet,pd.DataFrame):
			return sheet
		else:
			return [sheet]
	#特殊属性
	def has_flag(self,ID,*flags,split_symbol = "|"):
		"split_symbol参数无法通过位置指定"
		all_flags = self.get_property(ID,"Flags").split(split_symbol)
		for flag in flags:
			if flag in all_flags:
				return True
		return False

#实体
print("正在加载数据库...")
database = Database()
print("数据库加载成功！")