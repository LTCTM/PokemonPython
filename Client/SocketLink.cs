using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Xml.Linq;

namespace Client
{
    class SocketLink
    {
        //基本
        // 发送变长的数据，将数据长度附加于数据开头
        private static int SendVarData(Socket s, string content)
        {
            var data = Encoding.UTF8.GetBytes(content);
            int total = 0;
            int size = data.Length;  //要发送的消息长度
            int dataleft = size;     //剩余的消息
            int sent;
            //将消息长度（int类型）的，转为字节数组
            byte[] datasize = new byte[4];
            datasize = BitConverter.GetBytes(size);
            //将消息长度发送出去
            sent = s.Send(datasize);
            //发送消息剩余的部分
            while (total < size)
            {
                sent = s.Send(data, total, dataleft, SocketFlags.None);
                total += sent;
                dataleft -= sent;
            }
            return total;
        }
        // 接收变长的数据，要求其打头的4个字节代表有效数据的长度
        private static string ReceiveVarData(Socket s)
        {
            if (s == null)
                throw new ArgumentNullException("s");
            int total = 0;  //已接收的字节数
            int size = 0;
            int received = 0;
            //接收4个字节，得到“消息长度”
            byte[] datasize = new byte[4];
            s.Receive(datasize, 0, 4, 0);
            size = BitConverter.ToInt32(datasize, 0);
            //按消息长度接收数据
            int dataleft = size;
            byte[] data = new byte[size];
            while (total < size)
            {
                received = s.Receive(data, total, dataleft, 0);
                if (received == 0)
                {
                    break;
                }
                total += received;
                dataleft -= received;
            }
            return Encoding.UTF8.GetString(data, 0, data.Length);
        }
        //变量
        private const int port = 2345;
        private static Socket socketClient = null;
        private static IPAddress serverIP;
        private static int clearDelay;
        private static int reconnectTime;
        //初始化
        public static void Create()
        {
            //读取参数
            XDocument configFile = XDocument.Load("Config.xml");
            XElement root = configFile.Root;
            serverIP = IPAddress.Parse(root.Element("ServerIP").Value);
            clearDelay = int.Parse(root.Element("ClearDelay").Value);
            reconnectTime = int.Parse(root.Element("ReconnectTime").Value);
            if (reconnectTime < 250) reconnectTime = 250;
            //创建实例
            socketClient = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            IPEndPoint point = new IPEndPoint(serverIP, port);
            //进行连接
            Console.WriteLine("等待连接服务器……");
            while (true)
            {
                try
                {
                    socketClient.Connect(point);
                    break;
                }
                catch (SocketException)
                {
                    Thread.Sleep(reconnectTime);
                }
            }
            Console.WriteLine("成功连接服务器！");
        }
        private static string GetFromConsole()
        {
            return Console.ReadLine();
        }
        private static void Send()
        {
            SendVarData(socketClient, GetFromConsole());
        }
        //返回是否因为断线而结束
        public static bool Begin()
        {
            try
            {
                while (true)//send.Connected
                {
                    //获取发送过来的消息
                    string str = ReceiveVarData(socketClient);
                    if (str == "#Connect")
                    {

                    }
                    else if (str == "#Clear")
                        Console.Clear();
                    else if (str == "#TurnEnd")
                    {
                        if (clearDelay != 0)
                        {
                            Thread.Sleep(clearDelay);
                        }
                        else
                        {
                            Console.WriteLine("请按任意键继续");
                            Console.ReadKey();
                        }
                        Console.Clear();
                    }
                    else if (str == "#WantResponse")
                    {
                        Send();
                    }
                    else if (str == "#GameOver")
                    {
                        return false;
                    }
                    else if (str.Length >= 3 && str.Substring(0, 3) == "#AP")
                    {
                        var APArr = str.Split('|');
                        bool isHP = APArr[1] == "HP";
                        double currentAPRate = double.Parse(APArr[4]);

                        const int BAR_LENGTH = 24;
                        int APLength = (int)Math.Round(currentAPRate * BAR_LENGTH);
                        if (APLength < 1 && currentAPRate > 0)
                            APLength = 1;

                        Console.Write(APArr[1] + ": ");
                        Console.ForegroundColor = isHP ? ConsoleColor.Green : ConsoleColor.Blue;
                        string APBar = "";
                        for (int i = 1; i <= APLength; ++i)
                            APBar += "■";
                        for (int i = APLength + 1; i <= BAR_LENGTH; ++i)
                            APBar += "—";
                        Console.Write(APBar);
                        Console.ResetColor();
                        Console.WriteLine($" {APArr[2]}/{APArr[3]}");
                    }
                    else
                        Console.WriteLine(str);
                }
            }
            catch (SocketException ex)
            {
                Console.WriteLine("游戏发生了错误！错误信息：" + ex.Message);
            }
            return true;
        }
    }
}
