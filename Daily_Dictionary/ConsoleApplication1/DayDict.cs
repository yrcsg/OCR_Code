using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using MySql.Data.MySqlClient;
using System.Data;
using System.IO;
using System.Collections;
using System.Configuration;


namespace Daily
{
    class DayDict
    {
        //现阶段不考虑English Dictionary。把所有出现在transcripts和article里的词都加入daily dictionary
        static Hashtable dict=new Hashtable(); // dict is the English dictionary
        static int Max_trans = Convert.ToInt32(System.Configuration.ConfigurationSettings.AppSettings["Max_trans"]); // daily dictionary 中transcription的最大个数
        static int Max_articles = Convert.ToInt32(System.Configuration.ConfigurationSettings.AppSettings["Max_articles"]);
        static string OCR_Caption = System.Configuration.ConfigurationSettings.AppSettings["OCR_Caption"];
        static string Transcripts = System.Configuration.ConfigurationSettings.AppSettings["Transcripts"];
        static string GNewsCrawler = System.Configuration.ConfigurationSettings.AppSettings["GNewsCrawler"];
       // static string path_English_dict = System.Configuration.ConfigurationSettings.AppSettings["path_English_dict"];
        // this is the path of the txt contains the date that we will use to generate daily dictionary
        //static string path_Date = System.Configuration.ConfigurationSettings.AppSettings["path_Date"];
        static string path_Daily_Dict = System.Configuration.ConfigurationSettings.AppSettings["path_Daily_Dict"];
        

        static void Build_English_Dict(string path) 
        {
            string line;

            System.IO.StreamReader file =new System.IO.StreamReader(path);
            while ((line = file.ReadLine()) != null)
            {
                string[] line1 = line.Split('/');
                line = line1[0];
                if (!dict.Contains(line)) 
                {
                    dict.Add(line, line);
                }

            }
            file.Close();
        }


        static void Main(string[] args)
        {
            // path1 is the 100 id of correction testing
           // string path_dict = path_English_dict; // this is the path of the English dictionary.
           // Build_English_Dict(path_dict);
            //string Datefile = System.IO.File.ReadAllText(path_Date);
            //Console.WriteLine("haha+ " + Max_articles);
            //string[] Date = Datefile.Split('\n');// contains the date of daily dictionary
            //int date_num = Date.Length - 1;
            //string SQLsentence = "select * from VideoCaption where ";

            ////date_num = 10; // test

            //for (int i = 0; i < date_num; i++)
            //{
            //    if (i < date_num - 1)
            //    {
            //        SQLsentence = SQLsentence + @"ProgramName LIKE '%" + Date[i].Trim() + @"%' or ";
            //    }
            //    else { SQLsentence = SQLsentence + @"ProgramName LIKE '%" + Date[i].Trim() + @"%'"; }

            //}
            //Console.WriteLine(SQLsentence);
            //Console.ReadLine();

            DateTime TimeNow = DateTime.Now;
            string[] timenow1 = DateTime.Now.ToShortDateString().Split('/');
            string updateTime = timenow1[0] + '-' + timenow1[1] + '-' + timenow1[2];
            //Console.WriteLine(updateTime);

            MySqlConnection connection = new MySqlConnection(OCR_Caption);
            MySqlCommand cmd_conf = connection.CreateCommand();
            cmd_conf.CommandText = "select * from Configuration";
            MySqlDataAdapter adap_conf = new MySqlDataAdapter(cmd_conf);
            DataSet ds_conf = new DataSet();
            adap_conf.Fill(ds_conf);
            string startTime = "";
            string startCaption = "";
            foreach (DataRow dr_conf in ds_conf.Tables[0].Rows)
            {
                startTime = dr_conf[2].ToString();
                startCaption =dr_conf[4].ToString();
            }
            DateTime TimeBegin = Convert.ToDateTime(startTime);



            MySqlConnection connection2 = new MySqlConnection(GNewsCrawler);
            MySqlCommand cmd = connection.CreateCommand();
            cmd.CommandText = "select * from VideoCaption where id>"+startCaption;
           // cmd.CommandText = SQLsentence;
            MySqlDataAdapter adap = new MySqlDataAdapter(cmd);
            DataSet ds = new DataSet();
            adap.Fill(ds);
            int index = 0;

            foreach (DataRow dr in ds.Tables[0].Rows)
            {
                index++;
               // Console.WriteLine(index);
                //string programid = dr[1] + "_" + (dr[2]).ToString();

                //string[] pro = dr[1].ToString().Split('_');
                string[] array=dr[1].ToString().Split('_');
                int leng=array.Length;
                string time = array[leng - 2];
                Console.WriteLine(time);
                time = time.Substring(0, 4) + '-' + time.Substring(4, 2) + '-' + time.Substring(6, 2);
                DateTime dt = Convert.ToDateTime(time);
                if (DateTime.Compare(dt, TimeBegin) > 0 && DateTime.Compare(TimeNow, dt) > 0) 
                {
                    Console.WriteLine(time.Trim());
                    MySqlCommand cmd2 = connection2.CreateCommand();
                    cmd2.CommandText = "select * from Articles where pubDate='" + time + "'";
                    MySqlDataAdapter adap2 = new MySqlDataAdapter(cmd2);
                    DataSet ds2 = new DataSet();
                    adap2.Fill(ds2);
                    int number_articles = 1; // this is the number of articles in one day we used to build the dictionary
                    string article = "";
                    foreach (DataRow dr2 in ds2.Tables[0].Rows)
                    {
                        if (number_articles > Max_articles) { break; }
                        else
                        {
                            number_articles++;
                            article = article + dr2[1] + " " + dr2[4] + " ";
                        }
                    }
                    Console.WriteLine(article);
                    //Console.ReadLine();

                    MySqlConnection connection1 = new MySqlConnection(Transcripts);
                    MySqlCommand cmd1 = connection1.CreateCommand();
                    cmd1.CommandText = "select * from VideoStory where date(time)='" + time + "'";
                    MySqlDataAdapter adap1 = new MySqlDataAdapter(cmd1);
                    DataSet ds1 = new DataSet();
                    adap1.Fill(ds1);
                    int number_trans = 1;
                    string final = article; // final是最终写入daily dict的string
                    foreach (DataRow dr1 in ds1.Tables[0].Rows)
                    {

                        if (number_trans > Max_trans) { break; }
                        else
                        {
                            number_trans++;
                            Byte[] dt1 = (Byte[])dr1[6];
                            final = final + UnZipString(dt1);

                        }
                        string[] final1 = final.Split(' ');
                        final = "";
                        for (int j = 0; j < final1.Length; j++)
                        {
                            //Console.WriteLine(final1[j]);
                            //Console.WriteLine(!dict.Contains(final1[j].ToLower()));
                            if (final1[j].Length > 0 && !final1[j].Equals("..."))
                            {
                                //if (!dict.Contains(final1[j].ToLower()) && !dict.Contains(final1[j].ToLower().Substring(0, final1[j].Length - 1)))
                                //{
                                //  Console.WriteLine(!dict.Contains(final1[j]));
                                final = final + " " + final1[j];
                                //}
                            }

                        }
                        StreamWriter streamWriter = File.CreateText(path_Daily_Dict + time.Trim() + ".txt");
                        streamWriter.Write(final);
                        streamWriter.Close();
                        connection1.Close();
                        //Console.WriteLine();
                        //Console.ReadLine();
                    }
                }

                
                MySqlConnection MyConn2 = new MySqlConnection(OCR_Caption);
                if (!updateTime.Equals(""))
                {
                    string Query = "UPDATE `Configuration` SET `DailyTime`=\'" + updateTime + "\' WHERE id=1";
                    MySqlCommand MyCommand2 = new MySqlCommand(Query, MyConn2);
                    MySqlDataReader MyReader2;
                    MyConn2.Open();
                    MyReader2 = MyCommand2.ExecuteReader();
                    MyConn2.Close();
                }

                connection.Close();
                connection2.Close();




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
