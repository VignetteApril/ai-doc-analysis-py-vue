import sys
import os

# 确保能找到 app 目录
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

def create_admin():
    db = SessionLocal()
    try:
        # 检查是否已存在 admin
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print("❌ 管理员账号 'admin' 已存在。")
            return

        new_user = User(
            username="admin",
            hashed_password=hash_password("admin123"), # 默认密码
            is_active=True,
            is_superuser=True
        )
        db.add(new_user)
        db.commit()
        print("✅ 成功创建初始管理员账号！")
        print("用户名: admin")
        print("密  码: admin123")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()