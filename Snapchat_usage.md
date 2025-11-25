## Whole Process

手动使用Snapchat Ads的步骤必须要了解，这样才能实现自动化。

1. 去https://ads.snapchat.com/ 注册账号
2. 创建一个组织
3. 创建一个广告账户
4. 创建一个public profile
5. 关联snapchat到组织和profile
6. 创建一个Oauth App
7. 获得 token
8. 创建一个Ad Campaign
9. 创建一个Ad Squad
10. 创建一个creative
11. 创建一个Ad(如果没有绑定卡，public profile会失败)

## Get Token

## Ad Account

Go to Ad Account and add Leon as Admin

## Create Snapchat Ad Squad

```json
{
  "adsquads": [
    {
      "campaign_id": "f6f7c793-55aa-4c5a-a361-3645c8c6c858",
      "name": "Ad Squad Uno - Minimal",
      "type": "SNAP_ADS",
      "placement_v2": {
        "config": "AUTOMATIC"
      },
      "start_time": "2025-12-01T00:00:00.000Z",
      "end_time": "2026-01-01T00:00:00.000Z",
      "optimization_goal": "IMPRESSIONS",
      "billing_event": "IMPRESSION",
      "bid_micro": 20000000,
      "daily_budget_micro": 20000000,
      "bid_strategy": "LOWEST_COST_WITH_MAX_BID",
      "status": "ACTIVE",
      "targeting": {
        "geos": [
          {
            "country_code": "us"
          }
        ]
      }
    }
  ]
}
```

```json
{
  "adsquads": [
    {
      "name": "API Ad Squad - Minimal",
      "campaign_id": "f6f7c793-55aa-4c5a-a361-3645c8c6c858",
      "type": "SNAP_ADS",
      "placement_v2": {
        "config": "AUTOMATIC"
      },
      "start_time": "2025-12-01T00:00:00Z",
      "end_time": "2026-01-01T00:00:00Z",
      "optimization_goal": "IMPRESSIONS",
      "billing_event": "IMPRESSION",
      "bid_micro": 20000000,
      "daily_budget_micro": 20000000,
      "bid_strategy": "LOWEST_COST_WITH_MAX_BID",
      "status": "ACTIVE",
      "targeting": {
        "geos": [
          {
            "country_code": "us"
          }
        ],
        "demographics": [
          {
            "min_age": 18
          }
        ]
      }
    }
  ]
}
```