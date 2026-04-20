# 数据库设计

核心表：
- `users`：统一身份（patient/family/doctor/admin）
- `health_record`：血糖/血氧记录（`value_encrypted` 加密存储）
- `reminder`：用药/饮食提醒
- `message`：医患消息

说明：Web端与uni-app共用同一数据库实例，通过统一 REST API 访问。
