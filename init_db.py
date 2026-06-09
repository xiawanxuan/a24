import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app import models
from app import crud
from data.sample_data import get_sample_chars


def init_db():
    db_path = engine.url.database
    if db_path and db_path.startswith("sqlite:///"):
        db_file = db_path.replace("sqlite:///", "")
        if os.path.exists(db_file):
            print(f"数据库文件已存在: {db_file}")
            response = input("是否重建数据库？(y/N): ").strip().lower()
            if response == "y":
                os.remove(db_file)
                print("已删除旧数据库")
            else:
                print("取消初始化")
                return

    print("创建数据库表...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing_count = db.query(models.GuangyunChar).count()
        print(f"当前数据量: {existing_count} 条")

        if existing_count == 0:
            print("加载示例数据...")
            sample_chars = get_sample_chars()
            print(f"准备插入 {len(sample_chars)} 条数据...")

            created = crud.create_chars_bulk(db, sample_chars)

            final_count = db.query(models.GuangyunChar).count()
            print(f"数据插入完成，当前数据库共 {final_count} 条记录")

            shengmu_count = len(crud.get_all_shengmu(db))
            yunmu_count = len(crud.get_all_yunmu(db))
            she_count = len(crud.get_all_she(db))
            print(f"包含声母: {shengmu_count} 个，韵母: {yunmu_count} 个，韵摄: {she_count} 个")
        else:
            print("数据库已有数据，跳过数据填充")

    finally:
        db.close()

    print("数据库初始化完成！")


if __name__ == "__main__":
    init_db()
