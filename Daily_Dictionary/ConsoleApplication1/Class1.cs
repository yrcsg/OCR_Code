//using System;
//using System.Collections.Generic;
//using System.Linq;
//using System.Text;
//using MySql.Data.MySqlClient;
//using System.Data;
//using System.IO;


//namespace ConsoleApplication1
//{
//    class Class1
//    {

//        static void Main(string[] args)
//        {
//            // path1 is the 100 id of correction testing
//            string path1 = "E:\\OCR\\random_correct.txt";
//            string text = System.IO.File.ReadAllText(path1);
//            string[] text1 = text.Split('\n');// contains the 100 ids
//            string SQLsentence = "select * from VideoCaption where ";
//            for (int i = 0; i < 100; i++)
//            {
//                if (i < 99)
//                {
//                    SQLsentence = SQLsentence + "id=" + text1[i].Trim() + " or ";
//                }
//                else { SQLsentence = SQLsentence + "id=" + text1[i].Trim(); }

//            }
//            Console.WriteLine(SQLsentence);

//            string OCR_Caption = "Server=magicshadow.dvmm.org;Database=WikiEvent;Uid=ruichi;Pwd=2GejBcV7cvUNZGuY;";
//            string Transcripts = "Server=magicshadow.dvmm.org;Database=BroadcastNews;Uid=ruichi;Pwd=2GejBcV7cvUNZGuY;";
//            string GNewsCrawler = "Server=magicshadow.dvmm.org;Database=GNewsCrawler;Uid=ruichi;Pwd=2GejBcV7cvUNZGuY;";
//            MySqlConnection connection = new MySqlConnection(OCR_Caption);
//            MySqlConnection connection2 = new MySqlConnection(GNewsCrawler);
//            MySqlCommand cmd = connection.CreateCommand();
//            // cmd.CommandText = "select * from VideoCaption where id<100";
//            cmd.CommandText = SQLsentence;
//            MySqlDataAdapter adap = new MySqlDataAdapter(cmd);
//            DataSet ds = new DataSet();
//            adap.Fill(ds);
//            int index = 0;
//            foreach (DataRow dr in ds.Tables[0].Rows)
//            {
//                index++;
//                string programid = dr[1] + "_" + (dr[2]).ToString();
//                Console.WriteLine(programid);

//                string content = ""; // content is the overall transcript and articles of a given video

//                // use programid to find out event id
//                MySqlCommand cmd2 = connection.CreateCommand();
//                cmd2.CommandText = "select * from EventVideoLinking where videoId='" + programid + "'";
//                MySqlDataAdapter adap2 = new MySqlDataAdapter(cmd2);
//                DataSet ds2 = new DataSet();
//                adap2.Fill(ds2);
//                foreach (DataRow dr2 in ds2.Tables[0].Rows)
//                {
//                    //notice: one eventId has a lot of topicId
//                    string eventId = dr2[0].ToString();
//                    //Console.WriteLine("eventID: "+eventId);
//                    //Console.ReadLine();
//                    MySqlCommand cmd3 = connection.CreateCommand();
//                    cmd3.CommandText = "select * from EventTopicLinking where eventId='" + eventId + "'";
//                    MySqlDataAdapter adap3 = new MySqlDataAdapter(cmd3);
//                    DataSet ds3 = new DataSet();
//                    adap3.Fill(ds3);
//                    foreach (DataRow dr3 in ds3.Tables[0].Rows)
//                    {
//                        string TopicId = dr3[1].ToString();


//                        MySqlCommand cmd4 = connection2.CreateCommand();
//                        cmd4.CommandText = "select * from TopicArticle where topicId=" + TopicId;
//                        MySqlDataAdapter adap4 = new MySqlDataAdapter(cmd4);
//                        DataSet ds4 = new DataSet();
//                        adap4.Fill(ds4);
//                        int numb = 1; // this is the number of articles
//                        foreach (DataRow dr4 in ds4.Tables[0].Rows)
//                        {
//                            if (numb > 5)
//                            {
//                                break;
//                            }
//                            else
//                            {
//                                numb++;
//                                string articleId = dr4[1].ToString();

//                                MySqlCommand cmd5 = connection2.CreateCommand();
//                                cmd5.CommandText = "select * from Articles where id=" + articleId;
//                                MySqlDataAdapter adap5 = new MySqlDataAdapter(cmd5);
//                                DataSet ds5 = new DataSet();
//                                adap5.Fill(ds5);
//                                foreach (DataRow dr5 in ds5.Tables[0].Rows)
//                                {
//                                    content = content + dr5[1].ToString() + dr5[4].ToString();
//                                    Console.WriteLine("programid: " + programid + " eventID: " + eventId + " TopicID: " + TopicId + " ArticleId: " + articleId);
//                                    // Console.ReadLine();
//                                }
//                            }

//                        }

//                    }

//                }

//                MySqlConnection connection1 = new MySqlConnection(Transcripts);
//                MySqlCommand cmd1 = connection1.CreateCommand();
//                cmd1.CommandText = "select * from VideoStory where storyId='" + programid + "'";
//                MySqlDataAdapter adap1 = new MySqlDataAdapter(cmd1);
//                DataSet ds1 = new DataSet();
//                adap1.Fill(ds1);
//                string path = "E:\\OCR\\Project\\Transcripts1\\";
//                foreach (DataRow dr1 in ds1.Tables[0].Rows)
//                {
//                    Byte[] dt = (Byte[])dr1[6];
//                    StreamWriter streamWriter = File.CreateText(path + text1[index].Trim() + ".txt");
//                    streamWriter.Write(UnZipString(dt) + content);
//                    streamWriter.Close();
//                    Console.WriteLine(UnZipString(dt));
//                    //Console.ReadLine();
//                }
//                connection1.Close();
//            }
//            connection.Close();
//            connection2.Close();



//        }


//        public static byte[] ZipString(string text)
//        {
//            byte[] buffer = System.Text.Encoding.Unicode.GetBytes(text);
//            MemoryStream ms = new MemoryStream();
//            using (System.IO.Compression.GZipStream zip = new System.IO.Compression.GZipStream(ms, System.IO.Compression.CompressionMode.Compress, true))
//            {
//                zip.Write(buffer, 0, buffer.Length);
//            }

//            ms.Position = 0;
//            MemoryStream outStream = new MemoryStream();

//            byte[] compressed = new byte[ms.Length];
//            ms.Read(compressed, 0, compressed.Length);

//            byte[] gzBuffer = new byte[compressed.Length + 4];
//            System.Buffer.BlockCopy(compressed, 0, gzBuffer, 4, compressed.Length);
//            System.Buffer.BlockCopy(BitConverter.GetBytes(buffer.Length), 0, gzBuffer, 0, 4);
//            return gzBuffer;
//        }




//        public static string UnZipString(byte[] gzBuffer)
//        {
//            using (MemoryStream ms = new MemoryStream())
//            {
//                int msgLength = BitConverter.ToInt32(gzBuffer, 0);
//                ms.Write(gzBuffer, 4, gzBuffer.Length - 4);

//                byte[] buffer = new byte[msgLength];

//                ms.Position = 0;
//                using (System.IO.Compression.GZipStream zip = new System.IO.Compression.GZipStream(ms, System.IO.Compression.CompressionMode.Decompress))
//                {
//                    zip.Read(buffer, 0, buffer.Length);
//                }

//                return System.Text.Encoding.Unicode.GetString(buffer, 0, buffer.Length);
//            }
//        }


//    }
//}
