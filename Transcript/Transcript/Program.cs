using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using MySql.Data.MySqlClient;
using System.Data;
using System.IO;


namespace Transcript
{
    class Program
    {
        static string OCR_Caption = System.Configuration.ConfigurationSettings.AppSettings["OCR_Caption"];
        static string Transcripts = System.Configuration.ConfigurationSettings.AppSettings["Transcripts"];
        static string GNewsCrawler = System.Configuration.ConfigurationSettings.AppSettings["GNewsCrawler"];
        // this is the path of the txt contains the date that we will use to generate daily dictionary
        static string path_Transcript = System.Configuration.ConfigurationSettings.AppSettings["path_Transcript"];

        static void Main(string[] args)
        {
            MySqlConnection connection = new MySqlConnection(OCR_Caption);
            MySqlCommand cmd_conf = connection.CreateCommand();
            cmd_conf.CommandText = "select * from Configuration";
            MySqlDataAdapter adap_conf = new MySqlDataAdapter(cmd_conf);
            DataSet ds_conf = new DataSet();
            adap_conf.Fill(ds_conf);
            string startTranscriptID = "";
            string lockindex="";
            foreach (DataRow dr_conf in ds_conf.Tables[0].Rows)
            {
                startTranscriptID = dr_conf[1].ToString();
                lockindex = dr_conf[5].ToString();
            }

            if (lockindex.Equals("0")) // not locked
            {
                MySqlConnection connection11 = new MySqlConnection(OCR_Caption);
                string updateLock = "UPDATE `Configuration` SET `Lock_Transcript`=" + "1" + " WHERE id=1";
                MySqlCommand MyCommand3 = new MySqlCommand(updateLock, connection11);
                MySqlDataReader MyReader3;
                connection11.Open();
                MyReader3 = MyCommand3.ExecuteReader();
                connection11.Close();
                string SQLsentence = @"select * from VideoCaption where captionType !='HeadTitle' and id>" + startTranscriptID;
                Console.WriteLine(SQLsentence);
                Console.ReadLine();

                MySqlCommand cmd = connection.CreateCommand();
                cmd.CommandText = SQLsentence;
                MySqlDataAdapter adap = new MySqlDataAdapter(cmd);
                DataSet ds = new DataSet();
                adap.Fill(ds);
                int index = 0;
                string newid = "";
                //newid is the new transcript id which will be updated on Configuration table
                foreach (DataRow dr in ds.Tables[0].Rows)
                {
                    index++;
                    newid = dr[0].ToString();
                    string programid = dr[1] + "_" + (dr[2]).ToString();
                    Console.WriteLine(newid);
                    //Console.ReadLine();
                    MySqlConnection connection1 = new MySqlConnection(Transcripts);
                    MySqlCommand cmd1 = connection1.CreateCommand();
                    cmd1.CommandText = "select * from VideoStory where storyId='" + programid.Replace("\'", "\\'") + "'";
                    MySqlDataAdapter adap1 = new MySqlDataAdapter(cmd1);
                    DataSet ds1 = new DataSet();
                    adap1.Fill(ds1);
                    foreach (DataRow dr1 in ds1.Tables[0].Rows)
                    {
                        Byte[] dt = (Byte[])dr1[6];
                        StreamWriter streamWriter = File.CreateText(path_Transcript + dr[0].ToString() + ".txt");
                        streamWriter.Write(UnZipString(dt));
                        streamWriter.Close();
                        // Console.WriteLine(UnZipString(dt));
                    }
                    connection1.Close();
                }

                MySqlConnection MyConn2 = new MySqlConnection(OCR_Caption);
                if (!newid.Equals(""))
                {
                    string Query = "UPDATE `Configuration` SET `TranscriptID`=" + newid + " WHERE id=1";
                    string Query2 = "UPDATE `Configuration` SET `Lock_Transcript`=" + "0" + " WHERE id=1";
                    MySqlCommand MyCommand2 = new MySqlCommand(Query, MyConn2);
                    MySqlDataReader MyReader2;
                    MyConn2.Open();
                    MyReader2 = MyCommand2.ExecuteReader();
                    MyConn2.Close();

                    MyCommand2 = new MySqlCommand(Query2, MyConn2);
                    MyConn2.Open();
                    MyReader2 = MyCommand2.ExecuteReader();
                    MyConn2.Close();
                }
                connection.Close();
            }





            
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
