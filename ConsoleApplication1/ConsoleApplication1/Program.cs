//using System;
//using System.Collections.Generic;
//using System.Linq;
//using System.Text;
//using MySql.Data.MySqlClient;
//using System.Data;
//using System.IO;


//namespace ConsoleApplication1
//{
//    class Program
//    {

//        static void Main(string[] args)
//        {
//            string OCR_Caption = "Server=magicshadow.dvmm.org;Database=WikiEvent;Uid=ruichi;Pwd=2GejBcV7cvUNZGuY;";
//            string Transcripts = "Server=magicshadow.dvmm.org;Database=BroadcastNews;Uid=ruichi;Pwd=2GejBcV7cvUNZGuY;";
//            MySqlConnection connection = new MySqlConnection(OCR_Caption);
//            MySqlCommand cmd = connection.CreateCommand();
//            cmd.CommandText = "select * from VideoCaption where id<100";
//            MySqlDataAdapter adap = new MySqlDataAdapter(cmd);
//            DataSet ds = new DataSet();
//            adap.Fill(ds);
//            int index = 0;
//            foreach (DataRow dr in ds.Tables[0].Rows)
//            {
//                index++;
//                string programid = dr[1] + "_" + (dr[2]).ToString();
//                Console.WriteLine(programid);

//                //// use programid to find out event id
//                //MySqlCommand cmd2 = connection.CreateCommand();
//                //cmd2.CommandText = "select * from EventVideoLinking where videoId='"+programid+"'";
//                //MySqlDataAdapter adap2 = new MySqlDataAdapter(cmd2);
//                //DataSet ds2 = new DataSet();
//                //adap2.Fill(ds2);
//                //foreach (DataRow dr2 in ds2.Tables[0].Rows) 
//                //{
//                //    string eventId = dr2[0].ToString();
//                //    Console.WriteLine(eventId);
//                //}

//                MySqlConnection connection1 = new MySqlConnection(Transcripts);
//                MySqlCommand cmd1 = connection1.CreateCommand();
//                cmd1.CommandText = "select * from VideoStory where storyId='" + programid + "'";
//                MySqlDataAdapter adap1 = new MySqlDataAdapter(cmd1);
//                DataSet ds1 = new DataSet();
//                adap1.Fill(ds1);
//                string path = "E:\\OCR\\Project\\Transcripts\\";
//                foreach (DataRow dr1 in ds1.Tables[0].Rows)
//                {
//                    Byte[] dt = (Byte[])dr1[6];
//                    StreamWriter streamWriter = File.CreateText(path + index.ToString() + ".txt");
//                    streamWriter.Write(UnZipString(dt));
//                    streamWriter.Close();
//                    Console.WriteLine(UnZipString(dt));
//                    //Console.ReadLine();
//                }
//                connection1.Close();
//            }
//            connection.Close();


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
