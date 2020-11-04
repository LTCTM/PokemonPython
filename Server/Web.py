from socket import *
from Task import Task

BUFSIZE=1024

class GameConnection(object):
	@staticmethod
	def __send_ex(sender,message):
		message_bytes=bytes(message,"UTF-8")
		len_bytes=len(message_bytes).to_bytes(4,"little")
		sender.sendall(len_bytes+message_bytes)
	@staticmethod
	def __recv_ex(receiver):
		recv_msg=receiver.recv(BUFSIZE)
		msg_size=int.from_bytes(recv_msg[:4],"little")
		recv_msg=recv_msg[4:]
		recv_size=len(recv_msg)
		while recv_size<msg_size:
			recv_date=receiver.recv(BUFSIZE)
			recv_msg+=recv_date
			recv_size+=len(recv_date)
		return recv_msg.decode("UTF-8")
	def __init__(self):
		self.__player_names=[]
		self.__player_clients={}
		self.__player_files={}
		listener=socket()
		listener.bind(("",2345))
		print("开始监听")
		listener.listen(2)
		def connect_new_client(created_index):
			client,address=listener.accept()
			print("地址为"+address[0]+"的玩家连接成功")
			#测试
			DEFALUT_CONDITION=True
			#得到名字
			if DEFALUT_CONDITION:
				cur_name="玩家%d"%(created_index+1)
			else:
				GameConnection.__send_ex(client,"#CanRespond")
				GameConnection.__send_ex(client,"请输入您的姓名")
				cur_name=GameConnection.__recv_ex(client)
			#如果重名则改编
			if cur_name in self.__player_names:
				cur_name+="(2)"
			#得到文件名
			if DEFALUT_CONDITION:
				cur_file="t1.xml"
			else:
				GameConnection.__send_ex(client,"#CanRespond")
				GameConnection.__send_ex(client,"请输入您的队伍名")
				cur_file=GameConnection.__recv_ex(client)
			#装进数组
			self.__player_names.append(cur_name)
			self.__player_files[cur_name]=cur_file
			self.__player_clients[cur_name]=client
		listen_tasks=(Task.start_new(connect_new_client,(0,)),Task.start_new(connect_new_client,(1,)))
		Task.wait_all(listen_tasks)
		print("所有玩家连接成功")
	@property
	def player_names(self):
		return self.__player_names
	@property
	def player_files(self):
		return self.__player_files
	#target是player的名字
	def send_message(self,message,target_names,want_reponse):
		for target in target_names:
			GameConnection.__send_ex(self.__player_clients[target],message)
			if want_reponse:
				GameConnection.__send_ex(self.__player_clients[target],"#WantResponse")
	#target是player的名字
	def receive_message(self,target):
		return GameConnection.__recv_ex(self.__player_clients[target])

