# 糖尿病管理系统 / Diabetes Management System

基于 Flask + MySQL 的糖尿病患者管理系统，支持医生和管理员两种角色。

A Flask + MySQL diabetes patient management system with doctor and admin roles.

---

## 环境要求 / Requirements

- Python 3.9+
- MySQL 8.0+

---

## 安装步骤 / Installation

### 1. 克隆并进入项目目录

```bash
git clone <repository-url>
cd diabetes-system
```

### 2. 创建虚拟环境并安装依赖

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 3. 创建数据库

```sql
CREATE DATABASE diabetes_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入实际数据库连接信息和密钥
```

`.env` 示例:

```
SECRET_KEY=your-very-secret-key-change-this
DATABASE_URL=mysql+pymysql://root:password@localhost/diabetes_system
GLUCOSE_HIGH=11.1
GLUCOSE_LOW=3.9
```

### 5. 初始化并填充数据库

```bash
python seed.py
```

### 6. 启动应用

```bash
python run.py
```

访问 http://localhost:5000

---

## 演示账号 / Demo Accounts

| 角色   | 邮箱                   | 密码   |
|--------|------------------------|--------|
| 管理员 | admin@123.com          | 123456 |
| 医生1  | Doctor1@123.com        | 123456 |
| 医生2  | Doctor2@123.com        | 123456 |
| 医生3  | Doctor3@123.com        | 123456 |
| 医生4  | Doctor4@123.com        | 123456 |
| 医生5  | Doctor5@123.com        | 123456 |
| ...    | Doctor6~10@123.com     | 123456 |

---

## 路由说明 / Routes

### 认证
| 路径       | 方法      | 说明     |
|------------|-----------|----------|
| /login     | GET/POST  | 登录页面 |
| /logout    | GET       | 退出登录 |

### 医生端 (需要登录，doctor 角色)
| 路径                                    | 方法      | 说明             |
|-----------------------------------------|-----------|------------------|
| /doctor/dashboard                       | GET       | 医生仪表盘       |
| /doctor/patients                        | GET       | 我的患者列表     |
| /doctor/patients/\<id\>                 | GET/POST  | 患者详情及添加记录 |
| /doctor/patients/\<id\>/glucose_data    | GET       | 血糖图表JSON数据  |
| /doctor/reminders                       | GET/POST  | 提醒管理         |

### 管理员端 (需要登录，admin 角色)
| 路径                               | 方法      | 说明             |
|------------------------------------|-----------|------------------|
| /admin/dashboard                   | GET       | 管理员仪表盘     |
| /admin/dashboard/chart_data        | GET       | 图表JSON数据      |
| /admin/users                       | GET/POST  | 用户（医生）管理  |
| /admin/users/\<id\>/reset_password | POST      | 重置医生密码     |
| /admin/patients                    | GET/POST  | 全部患者管理     |
| /admin/patients/\<id\>/edit        | GET/POST  | 编辑患者信息     |

---

## 功能说明 / Features

- **医生端**：查看自己的患者列表，记录血糖和运动数据，通过 Chart.js 折线图查看趋势，创建患者提醒。
- **管理员端**：管理所有医生账号（添加、重置密码），管理所有患者（添加、编辑、分配医生），查看系统统计图表。
- **血糖预警**：血糖值 > 11.1 mmol/L 显示红色预警，< 3.9 mmol/L 显示黄色预警。

---

## 技术栈 / Tech Stack

- **后端**: Flask 3.0, Flask-SQLAlchemy, PyMySQL
- **前端**: Bootstrap 5, Chart.js 4, Bootstrap Icons
- **数据库**: MySQL 8.0
