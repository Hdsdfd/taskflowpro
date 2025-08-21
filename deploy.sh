#!/bin/bash

# TaskFlowPro 部署脚本
# 使用方法: ./deploy.sh

set -e

echo "开始部署 TaskFlowPro..."

# 设置变量
PROJECT_DIR="/var/www/taskflowpro"
VENV_DIR="$PROJECT_DIR/venv"
USER="www-data"

# 1. 更新代码（如果使用git）
# cd $PROJECT_DIR
# git pull origin main

# 2. 激活虚拟环境
source $VENV_DIR/bin/activate

# 3. 安装/更新依赖
echo "安装依赖..."
pip install -r requirements.txt

# 4. 设置环境变量
export DJANGO_SETTINGS_MODULE=TaskFlowPro.settings_production
export SECRET_KEY="your-production-secret-key-here"
export DB_NAME="taskflowpro"
export DB_USER="taskflowpro"
export DB_PASSWORD="your-db-password"
export DB_HOST="localhost"
export DB_PORT="5432"

# 5. 运行数据库迁移
echo "运行数据库迁移..."
python manage.py migrate

# 6. 收集静态文件
echo "收集静态文件..."
python manage.py collectstatic --noinput

# 7. 创建日志目录
mkdir -p $PROJECT_DIR/logs
mkdir -p /var/log/gunicorn
chown -R $USER:$USER $PROJECT_DIR/logs
chown -R $USER:$USER /var/log/gunicorn

# 8. 重启服务
echo "重启服务..."
sudo systemctl restart taskflowpro
sudo systemctl restart nginx

# 9. 检查服务状态
echo "检查服务状态..."
sudo systemctl status taskflowpro
sudo systemctl status nginx

echo "部署完成！"
echo "请访问: http://your-domain.com" 