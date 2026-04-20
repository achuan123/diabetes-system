# API 文档（Flask）

基础路径：`/api`

## 认证
- `POST /auth/web/register`：医生/管理员邮箱注册
- `POST /auth/web/login`：医生/管理员邮箱登录
- `POST /auth/patient/register`：患者手机号注册（可传 `doctor_id`）
- `POST /auth/patient/login`：患者手机号登录
- `POST /auth/family/register`：患者绑定家属（JWT）
- `POST /auth/family/login`：家属手机号登录

## 核心业务
- `GET /doctors`：患者注册时可选医生列表
- `POST /patient/records`：新增血糖/血氧
- `GET /patient/records`：查询记录（患者/家属查自己；医生/管理员按患者查）
- `POST /patient/reminders`、`GET /patient/reminders`：用药/饮食提醒
- `POST /messages`、`GET /messages`：医患消息

## 管理端
- `GET /admin/users`：管理员用户管理
- `GET /doctor/patients`：医生名下患者管理
