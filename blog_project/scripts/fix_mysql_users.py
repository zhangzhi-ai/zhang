import MySQLdb
from pathlib import Path

try:
    from decouple import Config, RepositoryEnv
except ImportError as exc:
    raise SystemExit("请先安装 python-decouple: pip install python-decouple") from exc


def load_db_config():
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        raise SystemExit(f"未找到 {env_path}，请先创建并填写数据库配置")
    config = Config(RepositoryEnv(env_path))
    return dict(
        host=config("DB_HOST", default="localhost"),
        user=config("DB_USER"),
        passwd=config("DB_PASSWORD"),
        db=config("DB_NAME"),
        port=int(config("DB_PORT", default=3306)),
        charset="utf8mb4",
    )


def column_exists(cursor, column):
    cursor.execute("SHOW COLUMNS FROM users LIKE %s", (column,))
    return cursor.fetchone() is not None


def main():
    params = load_db_config()
    conn = MySQLdb.connect(**params)
    cur = conn.cursor()

    alterations = []

    if not column_exists(cur, "is_superuser"):
        alterations.append(
            "ADD COLUMN is_superuser TINYINT(1) NOT NULL DEFAULT 0 AFTER last_login"
        )

    if not column_exists(cur, "first_name"):
        alterations.append(
            "ADD COLUMN first_name VARCHAR(150) NOT NULL DEFAULT '' AFTER username"
        )

    if not column_exists(cur, "last_name"):
        alterations.append(
            "ADD COLUMN last_name VARCHAR(150) NOT NULL DEFAULT '' AFTER first_name"
        )

    if not column_exists(cur, "date_joined"):
        alterations.append(
            "ADD COLUMN date_joined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER is_active"
        )

    if alterations:
        sql = "ALTER TABLE users " + ", ".join(alterations)
        print(sql)
        cur.execute(sql)

    # 调整 username 长度以符合 Django 默认配置
    cur.execute(
        "ALTER TABLE users MODIFY COLUMN username VARCHAR(150) NOT NULL COMMENT '用户名'"
    )

    conn.commit()
    cur.close()
    conn.close()
    print("users 表结构已更新")


if __name__ == "__main__":
    main()

