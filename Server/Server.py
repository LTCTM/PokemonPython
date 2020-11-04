from game import Game

def game_in_loop():
	restart = True
	while restart:
		try:
			game = Game()
			game.begin()
			restart = True if input("游戏结束！按1重新开始，其它关闭\n") == "1" else False
		except ConnectionError as e:
			print(e)
			restart = True if input("掉线！按1重新连接，其它关闭\n") == "1" else False


game_in_loop()