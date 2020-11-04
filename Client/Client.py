from socket import socket
from time import sleep
import os

def BUFSIZE():
	return 1024

class GameConnection(object):
	def send_ex(self,message):
		message_bytes=bytes(message,"UTF-8")
		len_bytes=len(message_bytes).to_bytes(4,"little")		
		self.__listener.send(len_bytes+message_bytes)
	def recv_ex(self):
		recv_msg=self.__listener.recv(BUFSIZE())
		msg_size=int.from_bytes(recv_msg[:4],"little")
		recv_msg=recv_msg[4:]
		recv_size=len(recv_msg)
		while recv_size<msg_size:
			recv_date=self.__listener.recv(BUFSIZE())
			recv_msg+=recv_date
			recv_size+=len(recv_date)
		return recv_msg.decode("UTF-8")
	def __init__(self):
		self.__listener=socket()
		print("等待服务器......")
		while True:
			try:
				self.__listener.connect(("127.0.0.1",2345))
				break;
			except:
				sleep(0.5)
		print("连接成功！")

def listen_in_loop():
	reconnect=True
	while reconnect:
		game_connection=GameConnection()
		try:
			while True:
				text=game_connection.recv_ex()
				if text=="#WantResponse":
					text=input("")
					game_connection.send_ex(text)
				elif text=="#Clear":
					print("\n"*5)
					pass
				else:
					print(text)
		except ConnectionError as e:
			print(e)
			reconnect =True if input("掉线！按1重新连接，其它关闭\n")=="1" else False
			os.system('cls')

listen_in_loop()
input("游戏结束！")
