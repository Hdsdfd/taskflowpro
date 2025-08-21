# TaskFlowPro 部署指南

## 概述
TaskFlowPro 是一个基于 Django 的任务流程管理系统。本文档将指导您如何将应用部署到云服务器上。

## 系统要求
- Ubuntu 20.04/22.04 LTS 或 CentOS 8+
- Python 3.8+
- Nginx
- PostgreSQL (推荐) 或 MySQL
- 至少 1GB RAM
- 至少 10GB 磁盘空间

## 部署步骤

### 1. 服务器环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础软件
sudo apt install python3 python3-pip python3-venv nginx git -y

# 安装 PostgreSQL
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. 配置数据库

```bash
# 切换到 postgres 用户
sudo -u postgres psql

# 创建数据库和用户
CREATE DATABASE taskflowpro;
CREATE USER taskflowpro WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE taskflowpro TO taskflowpro;
\q
```

### 3. 部署项目

```bash
# 创建项目目录
sudo mkdir -p /var/www/taskflowpro
sudo chown $USER:$USER /var/www/taskflowpro

# 上传项目文件（使用 git 或 scp）
cd /var/www/taskflowpro
git clone <your-repository-url> .

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制环境变量文件
cp env.example .env

# 编辑环境变量
nano .env
```

修改以下关键配置：
- `SECRET_KEY`: 生成新的密钥
- `ALLOWED_HOSTS`: 添加您的域名和服务器IP
- 数据库连接信息
- 邮件服务器配置

### 5. 配置 Django

```bash
# 设置环境变量
export DJANGO_SETTINGS_MODULE=TaskFlowPro.settings_production

# 运行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 收集静态文件
python manage.py collectstatic --noinput
```

### 6. 配置 Gunicorn

```bash
# 创建日志目录
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn

# 复制服务文件
sudo cp taskflowpro.service /etc/systemd/system/

# 重新加载 systemd
sudo systemctl daemon-reload

# 启用并启动服务
sudo systemctl enable taskflowpro
sudo systemctl start taskflowpro
```

### 7. 配置 Nginx

```bash
# 复制 Nginx 配置
sudo cp taskflowpro_nginx.conf /etc/nginx/sites-available/taskflowpro

# 创建符号链接
sudo ln -s /etc/nginx/sites-available/taskflowpro /etc/nginx/sites-enabled/

# 删除默认配置
sudo rm /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 8. 配置防火墙

```bash
# 允许 HTTP 和 HTTPS
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22

# 启用防火墙
sudo ufw enable
```

### 9. SSL 证书配置（可选但推荐）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取 SSL 证书
sudo certbot --nginx -d your-domain.com

# 设置自动续期
sudo crontab -e
# 添加以下行：
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 10. 测试部署

```bash
# 检查服务状态
sudo systemctl status taskflowpro
sudo systemctl status nginx
sudo systemctl status postgresql

# 查看日志
sudo journalctl -u taskflowpro -f
sudo tail -f /var/log/nginx/error.log
```

## 维护和更新

### 日常维护
```bash
# 备份数据库
pg_dump taskflowpro > backup_$(date +%Y%m%d).sql

# 更新代码
cd /var/www/taskflowpro
git pull origin main

# 运行部署脚本
./deploy.sh
```

### 监控
- 设置日志轮转
- 监控磁盘空间
- 监控内存使用
- 设置告警通知

## 故障排除

### 常见问题

1. **502 Bad Gateway**
   - 检查 Gunicorn 是否运行
   - 查看 Gunicorn 日志

2. **静态文件不显示**
   - 检查 STATIC_ROOT 配置
   - 重新运行 collectstatic

3. **数据库连接错误**
   - 检查数据库服务状态
   - 验证连接参数

4. **权限问题**
   - 检查文件权限
   - 确保 www-data 用户有适当权限

### 日志位置
- Django 日志: `/var/www/taskflowpro/logs/django.log`
- Gunicorn 日志: `/var/log/gunicorn/`
- Nginx 日志: `/var/log/nginx/`

## 安全建议

1. 定期更新系统和软件包
2. 使用强密码和密钥
3. 配置防火墙规则
4. 启用 HTTPS
5. 定期备份数据
6. 监控异常访问

## 性能优化

1. 启用 Nginx 缓存
2. 配置数据库连接池
3. 使用 CDN 加速静态文件
4. 启用 Gzip 压缩
5. 优化数据库查询

## 联系支持

如果遇到问题，请检查：
1. 系统日志
2. 应用日志
3. 网络连接
4. 配置文件语法 