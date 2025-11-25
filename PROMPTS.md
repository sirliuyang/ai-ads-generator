## 业务背景了解

在需求分析和POC的时候，发现需要先了解业务。

refer to:

- [Ads_Concept.md](./Ads_Concept.md)
- [Snapchat_usage.md](./Snapchat_usage.md) 

## 需求分析

实现一个自动生成flask app代码的AI项目，生成的代码可以接受用户输入的广告投放要求，并投放到用户要求的平台上。也就是用户需要先使用项目AI主程序生成代码，然后可以使用生成代码的api去请求投放广告。

### 主程序 - AI代码生成

输入: Platform name, documentation URL, and optional mock mode

```python
# Example usage - WITH mock auth (for testing without credentials)
agent.generate_api_client(
    platform="snapchat",
    docs_url="https://developers.snap.com/api/marketing-api/Ads-API/ads",
    mock_auth=True  # Returns mock responses, no real API calls
)

# Example usage - WITHOUT mock auth (production-ready code)
agent.generate_api_client(
    platform="snapchat",
    docs_url="https://developers.snap.com/api/marketing-api/Ads-API/ads"
    # No mock_auth - generates real API client that works with actual credentials
)
# Output: Creates snapchat_api.py with functions to create campaigns, ad squads, ads
```

**How it works**:

- Use tool calling to search/fetch API documentation
- Extract authentication, endpoints, request schemas, hierarchy
- Generate a Python module with functions like:
    - `create_campaign(account_id, name, budget, ...)`
    - `create_ad_squad(campaign_id, name, bid, ...)`
    - `create_ad(ad_squad_id, name, creative, ...)`
- **Optional mock mode**:
    - With `--mock-auth`: Generate code that returns mock responses (no real API calls, no credentials needed)
    - Without `--mock-auth`: Generate production-ready code that makes real API calls with proper authentication
- Save the generated code to a file (e.g., `snapchat_api.py`, `pinterest_api.py`)

这个项目实现后，需要测试三种模式：
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

### 生成的xxxx_api.py接口

对于不同的平台，生成不一样的API客户端，并使用这个客户端进行投放。具体的使用方式如下：

#### `POST /api/launch-campaign`

**Request Body Example**:

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

**Flask endpoint logic**:

```python
# Import the generated API client
from snapchat_api import create_campaign, create_ad_squad, create_ad


@app.route('/api/launch-campaign', methods=['POST'])
def launch_campaign():
    data = request.json

    # Use generated functions
    campaign = create_campaign(data['account_id'], data['campaign'])
    ad_squad = create_ad_squad(campaign['id'], data['ad_squads'][0])
    ad = create_ad(ad_squad['id'], data['ads'][0])

    return jsonify({
        "status": "success",
        "campaign_id": campaign['id'],
        "ad_squad_ids": [ad_squad['id']],
        "ad_ids": [ad['id']]
    })
```

## 架构设计

先提出一个自己的架构想法如下：

ai-ads-generator\
├── flask_api\
│   ├── app.py
│   └── config.py
│
├── generated_clients\
│
├── service\
│   ├── code_agent.py
│   ├── llm_remote.py
│   └── platform_doc_parser.py
│
├── tests\
│   ├── test_agent.py
│   └── test_clients.py
│
├── .env.example
├── .gitignore
├── PROMPTS.md
├── README.md
├── main.py
├── quickstart.sh
└── requirements.txt


然后让AI快速生成基础代码。