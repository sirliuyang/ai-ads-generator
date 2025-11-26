# Snapchat API 示例代码

下面是Snapchat API的实际使用示例，用于生成API客户端代码。

## 创建Campaign

```python
import requests
import json

url = "https://adsapi.snapchat.com/v1/adaccounts/22f54068-646f-4378-987b-dfb400d9e3c0/campaigns"

payload = json.dumps({
    "campaigns": [{
        "name": "API Campaign - Fixed Min Budget",
        "start_time": "2025-12-01T00:00:00Z",
        "end_time": "2026-01-01T00:00:00Z",
        "status": "ACTIVE",
        "objective": "WEB_CONVERSION",
        "daily_budget_micro": 20000000
    }]
})

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <token>'
}

response = requests.post(url, headers=headers, data=payload)
```

## 创建Ad Squad

```python
import requests
import json

url = "https://adsapi.snapchat.com/v1/campaigns/f6f7c793-55aa-4c5a-a361-3645c8c6c858/adsquads"

payload = json.dumps({
    "adsquads": [{
        "name": "API Ad Squad - Minimal",
        "campaign_id": "f6f7c793-55aa-4c5a-a361-3645c8c6c858",
        "type": "SNAP_ADS",
        "placement_v2": {"config": "AUTOMATIC"},
        "start_time": "2025-12-01T00:00:00Z",
        "end_time": "2026-01-01T00:00:00Z",
        "optimization_goal": "IMPRESSIONS",
        "billing_event": "IMPRESSION",
        "bid_micro": 20000000,
        "daily_budget_micro": 20000000,
        "bid_strategy": "LOWEST_COST_WITH_MAX_BID",
        "targeting": {
            "geos": [{"country_code": "us"}],
            "demographics": [{"min_age": 18}]
        }
    }]
})

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <token>'
}

response = requests.post(url, headers=headers, data=payload)
```

## 创建Media (两步)

### 第一步：创建Media对象

```python
import requests
import json

url = "https://adsapi.snapchat.com/v1/adaccounts/22f54068-646f-4378-987b-dfb400d9e3c0/media"

payload = json.dumps({
    "media": [{
        "name": "My Image Media",
        "type": "IMAGE"
    }]
})

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <token>'
}

response = requests.post(url, headers=headers, data=payload)
```

### 第二步：上传图片

```python
import requests

url = "https://adsapi.snapchat.com/v1/media/54926ca3-f79d-4f96-90e7-b0c621afef12/upload"

# 如果有图片文件
files = {'file': open('image.jpg', 'rb')}

headers = {
    'Authorization': 'Bearer <token>'
}

response = requests.post(url, headers=headers, files=files)
```

## 创建Creative

```python
import requests
import json

url = "https://adsapi.snapchat.com/v1/adaccounts/22f54068-646f-4378-987b-dfb400d9e3c0/creatives"

payload = json.dumps({
    "creatives": [{
        "name": "My First Creative via API",
        "ad_account_id": "22f54068-646f-4378-987b-dfb400d9e3c0",
        "type": "SNAP_AD",
        "top_snap_media_id": "54926ca3-f79d-4f96-90e7-b0c621afef12"
    }]
})

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <token>'
}

response = requests.post(url, headers=headers, data=payload)
```

## 创建Ad

```python
import requests
import json

url = "https://adsapi.snapchat.com/v1/adsquads/65f1d20c-694e-4737-acc0-77cfdd364eaa/ads"

payload = json.dumps({
    "ads": [{
        "name": "API Ad - Minimal",
        "ad_squad_id": "65f1d20c-694e-4737-acc0-77cfdd364eaa",
        "creative_id": "YOUR_CREATIVE_ID",
        "type": "SNAP_AD",
        "status": "PAUSED"
    }]
})

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <token>'
}

response = requests.post(url, headers=headers, data=payload)
```