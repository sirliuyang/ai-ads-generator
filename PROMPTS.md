## 需求分析

### 需求描述

实现一个自动生成flask app代码的AI项目，生成的代码可以接受用户输入的广告投放要求，并投放到用户要求的平台上。

### 输入输出

这个项目实现后，使用方法如下：
**Option A: Testing Mode (with mock auth)**, 也就是测试模式，不需要真实的API认证，只需要生成一个模拟的API客户端，然后使用这个客户端进行投放。

```bash
# Generate Snapchat API client with mocked responses
python agent.py --platform snapchat --docs https://developers.snap.com/api/marketing-api/Ads-API/ads --mock-auth
# Output: snapchat_api.py with mock responses, no credentials needed

# Test in Flask
curl -X POST http://localhost:5000/api/launch-campaign \
  -d '{"platform": "snapchat", "account_id": "test", ...}'
# Returns mock campaign_id, ad_squad_id, ad_id
```

**Option B: Production Mode (real API calls)**, 也就是生产模式，需要真实的API认证，然后使用这个客户端进行投放。

```bash
# Generate Snapchat API client for real API calls
python agent.py --platform snapchat --docs https://developers.snap.com/api/marketing-api/Ads-API/ads
# Output: snapchat_api.py with real OAuth/API authentication

# Use with real credentials
export SNAPCHAT_ACCESS_TOKEN="your-real-token"
curl -X POST http://localhost:5000/api/launch-campaign \
  -d '{"platform": "snapchat", "account_id": "real-account-id", ...}'
# Creates actual campaign on Snapchat
```

**Multi-Platform Support**, 也就是传入其他平台，比如Pinterest，只需要传入其他平台的文档链接，然后生成对应的API客户端，并使用这个客户端进行投放。

```bash
# Generate Pinterest client (production mode)
python agent.py --platform pinterest --docs https://developers.pinterest.com/docs/api/v5/
# Output: pinterest_api.py with real API calls

# Now Flask supports both platforms
# POST with platform="snapchat" → uses snapchat_api.py
# POST with platform="pinterest" → uses pinterest_api.py
```

### 生成的xxxx_api.py代码使用

#### 输入JSON

```json
{
  "platform": "snapchat",
  "account_id": "your-ad-account-id",
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
      "headline": "Summer Sale - 50% Off!",
      "image_url": "https://example.com/image.jpg"
    }
  ]
}
```

#### 输出

投放成功

## 实现架构