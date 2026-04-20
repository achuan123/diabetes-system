INSERT INTO users(role,name,email,password_hash)
VALUES ('doctor','默认医生','doctor@123.com','pbkdf2:sha256:600000$placeholder$placeholder')
ON CONFLICT(email) DO NOTHING;

INSERT INTO users(role,name,email,password_hash)
VALUES ('admin','系统管理员','admin@123','pbkdf2:sha256:600000$placeholder$placeholder')
ON CONFLICT(email) DO NOTHING;
