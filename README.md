# 使用指南

## 🚀 使用流程

### 步骤 1: 准备提示文件

参考根目录下面的两个提示文件:
snapchat_step1.md
snapchat_step2.txt

### 步骤 2: 生成API客户端

#### Mock模式

```bash
python -m src.main --platform snapchat --docs https://developers.snap.com/api/marketing-api/Ads-API/ads --mock-auth
```

输出：`generated_clients/snapchat_api.py`

#### 生产模式（Production）

生成真实API调用代码：

```bash
python -m src.main --platform snapchat --docs https://developers.snap.com/api/marketing-api/Ads-API/ads
```

## 🧪 测试

### 测试生成的代码

```bash
# 直接测试客户端
python src/generated_clients/snapchat_api.py
```

### 5. 测试API

#### 查看可用平台

```bash
curl http://localhost:5000/api/platforms
```

#### 投放广告活动

```bash
curl -X POST http://localhost:5000/api/launch-campaign \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "snapchat",
    "account_id": "test_account",
    "campaign": {
      "name": "Summer Sale 2024",
      "daily_budget_micro": 100000000
    },
    "ad_squads": [
      {
        "name": "Ad Squad 1",
        "bid_micro": 5000000
      }
    ],
    "ads": [
      {
        "name": "Summer Sale Ad 1",
        "headline": "50% Off!",
        "image_url": "https://example.com/image.jpg"
      }
    ]
  }'
```

## 使用场景

### 测试Flask API

```bash
# 1. 启动服务器
python src/flask_api/api.py

# 2. 测试端点
curl http://localhost:5000/api/platforms
curl -X POST http://localhost:5000/api/snapchat/launch-campaign -d '{...}'
```

### A. 测试模式（Mock Auth）

适用于：

- 开发和测试
- 无需真实API凭证
- 快速验证流程

```bash
# 生成Mock客户端
python main.py --platform snapchat --docs <url> --mock-auth

# 测试API调用
curl -X POST http://localhost:5000/api/launch-campaign \
  -H "Content-Type: application/json" \
  -d '{"platform": "snapchat", "account_id": "test", ...}'

# 返回模拟数据
{
  "status": "success",
  "campaign_id": "camp_mock_1234",
  "ad_squad_ids": ["squad_mock_5678"],
  "ad_ids": ["ad_mock_9012"]
}
```

### B. 生产模式（Production）

适用于：

- 真实广告投放
- 需要平台API凭证
- 生产环境部署

```bash
# 生成生产客户端
python main.py --platform snapchat --docs <url>

# 设置环境变量
export SNAPCHAT_ACCESS_TOKEN="your_real_token"

# 真实API调用
curl -X POST http://localhost:5000/api/launch-campaign \
  -H "Content-Type: application/json" \
  -d '{"platform": "snapchat", "account_id": "real_account", ...}'
```

### C. 多平台支持

```bash
# 生成Pinterest客户端
python main.py --platform pinterest \
  --docs https://developers.pinterest.com/docs/api/v5/

# 生成Facebook客户端
python main.py --platform facebook \
  --docs https://developers.facebook.com/docs/marketing-api

# Flask自动支持所有生成的平台
curl -X POST http://localhost:5000/api/launch-campaign \
  -d '{"platform": "pinterest", ...}'
```

## 🎓 最佳实践

### 1. 提示文件管理

```
项目根目录/
├── snapchat_step1.md
├── snapchat_step2.txt
├── pinterest_step1.md
├── pinterest_step2.txt
└── prompts/           # 可选：集中管理
```

### Flask配置

- 一次配置一个平台
- 测试后再添加下一个
- 保持代码清晰注释

## 🐛 故障排除

### 问题1: 提示文件未找到

```
⚠ 未找到 snapchat_step1 提示文件
```

**解决**: 在项目根目录创建 `snapchat_step1.md`

### 问题2: Stage 1生成失败

**检查**:

- OPENAI_API_KEY是否设置
- step1.md内容是否正确
- API文档是否可访问

### 问题3: Flask导入错误

```
ImportError: cannot import name 'launch_campaign'
```

**解决**:

1. 确认`snapchat_api.py`已生成
2. 检查文件中是否有`launch_campaign`函数
3. 重新生成代码

### 问题4: 路由404

**检查**:

1. Flask API中是否添加了路由
2. 路由路径是否正确
3. 重启Flask服务器

## 📚 相关文档

- `README.md` - 项目概述

## API文档

### POST /api/launch-campaign

## 许可

MIT License

## 联系方式

如有问题或建议，请提交Issue。
