#!/bin/bash

# TaskFlowPro 增强版部署脚本
# 包含所有新功能模块的部署

set -e

echo "🚀 开始部署 TaskFlowPro 增强版..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查Python版本
echo -e "${BLUE}检查Python版本...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo -e "${RED}错误: 需要Python 3.8或更高版本，当前版本: $python_version${NC}"
    exit 1
fi
echo -e "${GREEN}Python版本检查通过: $python_version${NC}"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${BLUE}创建虚拟环境...${NC}"
    python3 -m venv venv
fi

# 激活虚拟环境
echo -e "${BLUE}激活虚拟环境...${NC}"
source venv/bin/activate

# 升级pip
echo -e "${BLUE}升级pip...${NC}"
pip install --upgrade pip

# 安装依赖
echo -e "${BLUE}安装项目依赖...${NC}"
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}警告: 未找到.env文件，请确保已配置环境变量${NC}"
fi

# 设置Django环境
export DJANGO_SETTINGS_MODULE=TaskFlowPro.settings

# 检查数据库连接
echo -e "${BLUE}检查数据库连接...${NC}"
python manage.py check --database default

# 创建数据库迁移
echo -e "${BLUE}创建数据库迁移...${NC}"
python manage.py makemigrations users
python manage.py makemigrations projects
python manage.py makemigrations tasks
python manage.py makemigrations comments
python manage.py makemigrations files
python manage.py makemigrations notifications
python manage.py makemigrations analytics
python manage.py makemigrations workflows
python manage.py makemigrations calendar
python manage.py makemigrations api
python manage.py makemigrations integrations

# 应用迁移
echo -e "${BLUE}应用数据库迁移...${NC}"
python manage.py migrate

# 收集静态文件
echo -e "${BLUE}收集静态文件...${NC}"
python manage.py collectstatic --noinput

# 创建超级用户（如果不存在）
echo -e "${BLUE}检查超级用户...${NC}"
if ! python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(is_superuser=True).exists()" 2>/dev/null; then
    echo -e "${YELLOW}未找到超级用户，请手动创建:${NC}"
    echo "python manage.py createsuperuser"
fi

# 检查Celery配置
echo -e "${BLUE}检查Celery配置...${NC}"
if command -v redis-server &> /dev/null; then
    echo -e "${GREEN}Redis已安装${NC}"
else
    echo -e "${YELLOW}警告: Redis未安装，异步任务功能将不可用${NC}"
    echo "请安装Redis: sudo apt install redis-server"
fi

# 创建必要的目录
echo -e "${BLUE}创建必要的目录...${NC}"
mkdir -p media/project_files
mkdir -p media/file_versions
mkdir -p media/avatars
mkdir -p logs

# 设置文件权限
echo -e "${BLUE}设置文件权限...${NC}"
chmod 755 media/
chmod 755 logs/

# 检查服务状态
echo -e "${BLUE}检查服务状态...${NC}"
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}Nginx服务正在运行${NC}"
else
    echo -e "${YELLOW}Nginx服务未运行，请检查配置${NC}"
fi

if systemctl is-active --quiet gunicorn; then
    echo -e "${GREEN}Gunicorn服务正在运行${NC}"
else
    echo -e "${YELLOW}Gunicorn服务未运行，请检查配置${NC}"
fi

# 运行系统检查
echo -e "${BLUE}运行系统检查...${NC}"
python manage.py check --deploy

# 创建部署完成标记
echo -e "${BLUE}创建部署完成标记...${NC}"
echo "部署完成时间: $(date)" > .deployed
echo "部署版本: $(git rev-parse HEAD 2>/dev/null || echo '未知')" >> .deployed

echo -e "${GREEN}✅ TaskFlowPro 增强版部署完成！${NC}"
echo ""
echo -e "${BLUE}下一步操作:${NC}"
echo "1. 启动Celery工作进程: celery -A TaskFlowPro worker -l info"
echo "2. 启动Celery调度器: celery -A TaskFlowPro beat -l info"
echo "3. 访问管理后台: http://your-domain/admin/"
echo "4. 检查日志文件: tail -f logs/django.log"
echo ""
echo -e "${BLUE}新功能模块:${NC}"
echo "✅ 文件管理系统"
echo "✅ 智能通知系统"
echo "✅ 数据分析报告"
echo "✅ 工作流审批"
echo "✅ 日历管理"
echo "✅ 移动端API"
echo "✅ 第三方集成"
echo ""
echo -e "${GREEN}🎉 享受使用 TaskFlowPro 增强版！${NC}"
