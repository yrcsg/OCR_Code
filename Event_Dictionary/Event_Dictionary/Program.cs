using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using MySql.Data.MySqlClient;
using System.Data;
using System.IO;


namespace Event_Dictionary
{
    class Program{

        static int Max_articles = Convert.ToInt32(System.Configuration.ConfigurationSettings.AppSettings["Max_articles"]);
        static string OCR_Caption = System.Configuration.ConfigurationSettings.AppSettings["OCR_Caption"];
        static string Transcripts = System.Configuration.ConfigurationSettings.AppSettings["Transcripts"];
        static string GNewsCrawler = System.Configuration.ConfigurationSettings.AppSettings["GNewsCrawler"];
        static string path_Event_Dict = System.Configuration.ConfigurationSettings.AppSettings["path_Event_Dict"];

        static void Main(string[] args)
        {

            MySqlConnection connection = new MySqlConnection(OCR_Caption);
            MySqlConnection connection2 = new MySqlConnection(GNewsCrawler);

            MySqlCommand cmd_conf = connection.CreateCommand();
            cmd_conf.CommandText = "select * from Configuration";
            MySqlDataAdapter adap_conf = new MySqlDataAdapter(cmd_conf);
            DataSet ds_conf = new DataSet();
            adap_conf.Fill(ds_conf);
            string startEventID = "";
            foreach (DataRow dr_conf in ds_conf.Tables[0].Rows) 
            {
                startEventID = dr_conf[3].ToString();
            }


            MySqlCommand cmd = connection.CreateCommand();
            cmd.CommandText = "select distinct(eventId) from EventTopicLinking where eventId>"+startEventID;
            MySqlDataAdapter adap = new MySqlDataAdapter(cmd);
            DataSet ds = new DataSet();
            adap.Fill(ds);
            int index = 0;
            string newid = "";
            foreach (DataRow dr in ds.Tables[0].Rows)
            {
                index++;
                string eventId = dr[0].ToString();
                Console.WriteLine(eventId);
                newid = eventId;
                string content = ""; // content is the event related transcript and articles of a given eventId
                MySqlCommand cmd3 = connection.CreateCommand();
                cmd3.CommandText = "select * from EventTopicLinking where eventId='" + eventId + "'";
                MySqlDataAdapter adap3 = new MySqlDataAdapter(cmd3);
                DataSet ds3 = new DataSet();
                adap3.Fill(ds3);
                foreach (DataRow dr3 in ds3.Tables[0].Rows)
                {
                    string TopicId = dr3[1].ToString();
                    MySqlCommand cmd4 = connection2.CreateCommand();
                    cmd4.CommandText = "select * from TopicArticle where topicId=" + TopicId;
                    MySqlDataAdapter adap4 = new MySqlDataAdapter(cmd4);
                    DataSet ds4 = new DataSet();
                    adap4.Fill(ds4);
                    int numb = 1; // this is the number of articles
                    foreach (DataRow dr4 in ds4.Tables[0].Rows)
                    {
                       if (numb > Max_articles)
                       {
                           break;
                       }
                       else
                       {
                           numb++;
                           string articleId = dr4[1].ToString();
                           MySqlCommand cmd5 = connection2.CreateCommand();
                           cmd5.CommandText = "select * from Articles where id=" + articleId;
                           MySqlDataAdapter adap5 = new MySqlDataAdapter(cmd5);
                           DataSet ds5 = new DataSet();
                           adap5.Fill(ds5);
                           foreach (DataRow dr5 in ds5.Tables[0].Rows)
                           {
                               content = content + dr5[1].ToString() + dr5[4].ToString();
                               //Console.WriteLine( " eventID: " + eventId + " TopicID: " + TopicId + " ArticleId: " + articleId);
                            }
                        }
                    }
                }// 到此，已经把所有event相关文章建成字典

                MySqlCommand cmd2 = connection.CreateCommand();
                cmd2.CommandText = "select * from EventVideoLinking where eventId='" + eventId + "'";
                MySqlDataAdapter adap2 = new MySqlDataAdapter(cmd2);
                DataSet ds2 = new DataSet();
                adap2.Fill(ds2);
                foreach (DataRow dr2 in ds2.Tables[0].Rows)
                {
                    string videoId = dr2[1].ToString();
                    MySqlConnection connection1 = new MySqlConnection(Transcripts);
                    MySqlCommand cmd1 = connection1.CreateCommand();
                    cmd1.CommandText = "select * from VideoStory where storyId='" + videoId.Replace("\'","\\'") + "'";
                    MySqlDataAdapter adap1 = new MySqlDataAdapter(cmd1);
                    DataSet ds1 = new DataSet();
                    adap1.Fill(ds1);
                    foreach (DataRow dr1 in ds1.Tables[0].Rows)
                    {
                        Byte[] dt = (Byte[])dr1[6];
                        content = content + UnZipString(dt);
                    }
                    connection1.Close();
                }
                StreamWriter streamWriter = File.CreateText(path_Event_Dict + eventId.Trim() + ".txt");
                Console.WriteLine(content.IndexOf("..."));
                content.Replace("Antarctic", "hhhhhhh");
                Console.WriteLine(content.IndexOf("..."));
                streamWriter.Write(content);
                streamWriter.Close();
           }
            connection.Close();

            MySqlConnection MyConn2 = new MySqlConnection(OCR_Caption);
            if (!newid.Equals("")) 
            {
                string Query = "UPDATE `Configuration` SET `TranscriptID`=" + newid + " WHERE id=1";
                MySqlCommand MyCommand2 = new MySqlCommand(Query, MyConn2);
                MySqlDataReader MyReader2;
                MyConn2.Open();
                MyReader2 = MyCommand2.ExecuteReader();
                MyConn2.Close();
            }
            

            connection2.Close();

        }


        public static byte[] ZipString(string text)
        {
            byte[] buffer = System.Text.Encoding.Unicode.GetBytes(text);
            MemoryStream ms = new MemoryStream();
            using (System.IO.Compression.GZipStream zip = new System.IO.Compression.GZipStream(ms, System.IO.Compression.CompressionMode.Compress, true))
            {
                zip.Write(buffer, 0, buffer.Length);
            }

            ms.Position = 0;
            MemoryStream outStream = new MemoryStream();

            byte[] compressed = new byte[ms.Length];
            ms.Read(compressed, 0, compressed.Length);

            byte[] gzBuffer = new byte[compressed.Length + 4];
            System.Buffer.BlockCopy(compressed, 0, gzBuffer, 4, compressed.Length);
            System.Buffer.BlockCopy(BitConverter.GetBytes(buffer.Length), 0, gzBuffer, 0, 4);
            return gzBuffer;
        }




        public static string UnZipString(byte[] gzBuffer)
        {
            using (MemoryStream ms = new MemoryStream())
            {
                int msgLength = BitConverter.ToInt32(gzBuffer, 0);
                ms.Write(gzBuffer, 4, gzBuffer.Length - 4);

                byte[] buffer = new byte[msgLength];

                ms.Position = 0;
                using (System.IO.Compression.GZipStream zip = new System.IO.Compression.GZipStream(ms, System.IO.Compression.CompressionMode.Decompress))
                {
                    zip.Read(buffer, 0, buffer.Length);
                }

                return System.Text.Encoding.Unicode.GetString(buffer, 0, buffer.Length);
            }
        }


    }
}