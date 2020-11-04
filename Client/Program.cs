using System;

namespace Client
{
    class Program
    {
        static void Main(string[] args)
        {
            bool restart = true;
            while(restart)
            {
                Console.Clear();
                SocketLink.Create();
                SocketLink.Begin();
                Console.WriteLine("是否重新开始游戏？0：是 1：否");
                string result = Console.ReadLine();
                restart = (result == "0" ? true : false);
            } 
        }
    }
}
