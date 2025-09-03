# TaskFlowPro 数据库迁移指南

## 概述
本文档指导您如何为新添加的功能模块创建和运行数据库迁移。

## 迁移步骤

### 1. 创建迁移文件
```bash
# 为所有新应用创建迁移文件
python manage.py makemigrations files
python manage.py makemigrations notifications
python manage.py makemigrations analytics
python manage.py makemigrations workflows
python manage.py makemigrations calendar
python manage.py makemigrations api
python manage.py makemigrations integrations

# 或者一次性为所有应用创建迁移
python manage.py makemigrations
```

### 2. 检查迁移文件
```bash
# 查看待应用的迁移
python manage.py showmigrations

# 查看特定迁移的SQL语句
python manage.py sqlmigrate files 0001
```

### 3. 应用迁移
```bash
# 应用所有迁移
python manage.py migrate

# 或者应用特定应用的迁移
python manage.py migrate files
python manage.py migrate notifications
python manage.py migrate analytics
python manage.py migrate workflows
python manage.py migrate calendar
python manage.py migrate api
python manage.py migrate integrations
```

### 4. 验证迁移
```bash
# 检查数据库状态
python manage.py dbshell

# 在数据库shell中查看表
\dt

# 退出数据库shell
\q
```

## 新功能模块说明

### 文件管理 (files)
- 文件上传、分类、版本管理
- 文件评论和权限控制
- 支持多种文件类型

### 通知系统 (notifications)
- 多渠道通知（邮件、站内、推送）
- 通知模板和个性化设置
- 免打扰时间设置

### 数据分析 (analytics)
- 项目进度和绩效报告
- 团队效率分析
- 数据导出和缓存

### 工作流 (workflows)
- 可配置的审批流程
- 多步骤工作流
- 审批请求管理

### 日历管理 (calendar)
- 团队日历和事件管理
- 会议安排和出勤记录
- 重复事件支持

### API支持 (api)
- RESTful API接口
- 移动端支持
- 推送通知和离线同步

### 第三方集成 (integrations)
- Git仓库集成
- Webhook支持
- 数据同步功能

## 注意事项

1. **备份数据库**: 迁移前请备份现有数据库
2. **测试环境**: 建议先在测试环境运行迁移
3. **依赖关系**: 注意应用间的依赖关系
4. **数据完整性**: 迁移后检查数据完整性

## 故障排除

### 常见问题

1. **迁移冲突**: 删除冲突的迁移文件，重新创建
2. **字段类型不匹配**: 检查模型字段定义
3. **外键约束**: 确保关联表存在

### 回滚迁移
```bash
# 回滚到特定迁移
python manage.py migrate files 0001

# 回滚所有迁移
python manage.py migrate files zero
```

## 生产环境部署

1. **维护窗口**: 选择低峰期进行迁移
2. **监控**: 迁移过程中监控系统状态
3. **回滚计划**: 准备回滚方案
4. **测试**: 迁移后进行全面测试
