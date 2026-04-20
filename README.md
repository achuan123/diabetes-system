# 社区糖尿病患者管理系统

## 目录
- `backend/` Flask 后端（JWT + SQLAlchemy + 加密存储）
- `web-admin/` Vue3 + Element Plus 医生/管理员管理端
- `mobile-app/` uni-app 患者/家属端骨架
- `database/` SQL 脚本
- `docs/` API、数据库、用户手册、部署文档

## 默认账号
- 医生：`doctor@123.com / doctor123456`
- 管理员：`admin@123 / admin123456`

## 快速启动
```bash
pip install -r backend/requirements.txt
python backend/app.py
```

健康检查：`GET /health`
