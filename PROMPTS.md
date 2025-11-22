## 需求分析

### 需求描述

自动生成flask app代码，该代码可以接受用户输入的广告投放要求，并投放到用户要求的平台上

### 输入输出

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