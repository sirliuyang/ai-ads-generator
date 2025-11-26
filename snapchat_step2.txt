Snapchat广告投放完整工作流

用户输入JSON格式:
{
  "account_id": "ad-account-id",
  "campaign": {
    "name": "Summer Sale 2024",
    "daily_budget_micro": 100000000
  },
  "ad_squads": [{
    "name": "Ad Squad 1",
    "bid_micro": 5000000
  }],
  "ads": [{
    "name": "Summer Sale Ad 1",
    "headline": "Summer Sale - 50% Off!",
    "image_url": "https://example.com/image.jpg"
  }]
}

launch_campaign函数需要执行6个步骤:

步骤1: 创建Campaign
- 调用: create_campaign(account_id, **campaign_data)
- 参数: account_id + campaign中的所有字段
- 返回: campaign_id

步骤2: 创建Ad Squad
- 调用: create_ad_squad(campaign_id, account_id, **ad_squad_data)
- 参数: campaign_id + account_id + ad_squads[0]中的所有字段
- 返回: squad_id

对于ads数组中的每个ad，执行步骤3-6:

步骤3: 创建Media
- 调用: create_media(account_id, name=ad['name'], type='IMAGE')
- 参数: account_id + 基本media信息
- 返回: media_id

步骤4: 上传图片
- 调用: upload_media(media_id, image_url=ad['image_url'])
- 参数: media_id + image_url
- 注意: 如果image_url是网络URL，需要先下载
- 返回: 上传状态

步骤5: 创建Creative
- 调用: create_creative(account_id, media_id=media_id, **ad_data)
- 参数: account_id + media_id + ad中的其他字段(headline等)
- 返回: creative_id

步骤6: 创建Ad
- 调用: create_ad(squad_id, account_id, creative_id=creative_id, **ad_data)
- 参数: squad_id + account_id + creative_id + ad中的其他字段
- 返回: ad_id

返回值结构:
{
  "status": "success" | "partial" | "failed",
  "campaign_id": "campaign_xxx",
  "ad_squad_ids": ["squad_xxx"],
  "media_ids": ["media_xxx"],
  "creative_ids": ["creative_xxx"],
  "ad_ids": ["ad_xxx"],
  "errors": []
}

错误处理:
- 使用try-except包裹每个步骤
- 如果某步失败，记录错误并继续
- 返回status='partial'表示部分成功
- errors数组包含所有错误信息

重要注意事项:
1. 所有步骤必须按顺序执行
2. 前一步的ID是后一步的输入
3. 如果有多个ads，为每个ad重复步骤3-6
4. 如果campaign创建失败，返回status='failed'
5. 如果campaign成功但ad创建失败，返回status='partial'