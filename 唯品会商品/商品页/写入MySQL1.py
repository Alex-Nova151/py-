import pandas as pd
import pymysql
from sqlalchemy import create_engine


def create_mysql_db(db_name, user='root', password='root', host='127.0.0.1', port=3306):
    """
    自动创建MySQL数据库（如果不存在）
    """
    # 连接MySQL服务器（不指定具体数据库）
    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        charset='utf8mb4'
    )
    with conn.cursor() as cursor:
        # 创建数据库（避免重复创建）
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print(f"✅ 数据库 {db_name} 创建/检查完成")
    conn.close()


def load_cleaned_data_to_mysql():
    """
    读取清洗后的CSV文件，批量写入MySQL数据库
    """
    # ===================== 1. 配置信息（根据你的实际情况修改） =====================
    MYSQL_CONFIG = {
        'user': 'root',  # 你的MySQL用户名
        'password': 'root',  # 你的MySQL密码
        'host': '127.0.0.1',  # MySQL主机（本地填127.0.0.1）
        'port': 3306,  # MySQL端口（默认3306）
        'db_name': '京东商品',  # 要创建/使用的数据库名
        'table_name': '唯品会商品手机'  # 要创建的数据表名
    }

    # ===================== 2. 自动创建数据库 =====================
    create_mysql_db(
        db_name=MYSQL_CONFIG['db_name'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password'],
        host=MYSQL_CONFIG['host'],
        port=MYSQL_CONFIG['port']
    )

    # ===================== 3. 读取清洗后的CSV文件 =====================
    # 读取你之前清洗好的文件（路径和清洗脚本保持一致）
    cleaned_csv_path = '唯品会手机商品.csv'
    df = pd.read_csv(cleaned_csv_path)
    print(f"📊 成功读取清洗后的数据，共 {len(df)} 行")

    # ===================== 4. 创建MySQL连接引擎（适配pandas to_sql） =====================
    # 连接格式：mysql+pymysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4
    engine = create_engine(
        f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['db_name']}?charset=utf8mb4"
    )

    # ===================== 5. 批量写入MySQL =====================
    print(f"🚀 开始批量写入数据到 {MYSQL_CONFIG['db_name']}.{MYSQL_CONFIG['table_name']}...")
    df.to_sql(
        name=MYSQL_CONFIG['table_name'],  # 要写入的数据表名
        con=engine,  # 数据库连接引擎
        if_exists='replace',  # 表存在则覆盖（首次用replace，后续追加用append）
        index=False,  # 不把pandas的索引写入数据库
        chunksize=1000  # 分批写入（数据量大时避免卡死）
    )
    print("✅ 数据批量写入完成！")

    # ===================== 6. 验证数据是否写入成功 =====================
    # 连接MySQL验证
    conn = pymysql.connect(
        host=MYSQL_CONFIG['host'],
        port=MYSQL_CONFIG['port'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password'],
        database=MYSQL_CONFIG['db_name'],
        charset='utf8mb4'
    )
    with conn.cursor() as cursor:
        # 查询表的总行数
        cursor.execute(f"SELECT COUNT(*) FROM {MYSQL_CONFIG['table_name']}")
        row_count = cursor.fetchone()[0]
        print(f"🔍 验证：数据库表中现有 {row_count} 行数据（和CSV行数 {len(df)} 一致则说明写入成功）")

        # 查询前5条数据示例
        cursor.execute(f"SELECT 标题, 销量, 原价 FROM {MYSQL_CONFIG['table_name']} LIMIT 5")
        print("\n📝 数据库中前5条数据示例：")
        for idx, row in enumerate(cursor.fetchall(), 1):
            print(f"{idx}. 标题：{row[0][:20]}... | 销量：{row[1]} | 原价：{row[2]}")

    conn.close()
    engine.dispose()  # 关闭引擎连接


# 执行入库函数
if __name__ == "__main__":
    load_cleaned_data_to_mysql()