import config as conf
import pandas as pd

from sqlalchemy import create_engine, text
# from supabase import create_client, Client

DB_CONNECTION_STR = conf.DB_CONNECTION_STR

engine = create_engine(DB_CONNECTION_STR)

SOURCE_TABLE = "News_data"

def get_data(engine, SQL = "") -> pd.Dataframe: 
    """
    讀取資料(read):
    1. 給定SQL抓取特定資料
    2. 不給定SQL抓取全部資料庫
    """
    try:
        df_read = pd.read_sql(SQL, engine) if SQL else pd.read_sql(SOURCE_TABLE, engine)
        return df_read

    except Exception as e:
        print(f"讀取失敗: {e}")
        return pd.DataFrame


def put_data(engine, put_data_dict = None, modi_data_dict = None):
    """
    寫入新資料(write)格式如下:
    dict: {
        "url": 文章網址,
        "source": 文章來源(網站名),
        "title": 文章標題,
        "category": 文章分類(新聞, 經濟, 社交媒體), 
        "news_data": 新聞發布日期,
        "add_date": 加入資料庫日期,
        "content": 新聞內文
    }
    修改資料:
    確保欲修改資料之url存在，將複寫原資料
    """
    try:
        if put_data_dict:
            df_write = pd.DataFrame(put_data_dict)
            df_write.to_sql(SOURCE_TABLE, engine, if_exists="append", index=False)

        if modi_data_dict:
            target_url = modi_data_dict.get("url")
            if not target_url:
                raise ValueError("修改資料失敗：缺少 'url' 作為索引鍵")
            
            with engine.begin() as conn:
                update_fields = ", ".join([f"{k} = :{k}" for k in modi_data_dict.keys() if k != "url"])
                
                sql_query = text(f"""
                    UPDATE "{SOURCE_TABLE}"
                    SET {update_fields}
                    WHERE url = :url
                """)

                result = conn.execute(sql_query, modi_data_dict)
                
                if result.rowcount > 0:
                    print(f"修改資料成功 (影響 {result.rowcount} 筆): {target_url}")
                else:
                    print(f"修改無效：找不到 URL 為 {target_url} 的資料")
    except Exception as e:
        print(f"Error occured in: put_data: {e}")
        
