## Snapchat

### 广告概念
Snapchat的广告账户采用Campaign（广告系列） → Ad Squad（广告组） → Ad（广告） 的三级结构。这种设计旨在系统化地管理广告活动，其结构和设计逻辑如下表所示：

| 层级                     | 核心功能与设置内容                             | 设计逻辑与目的                                              |
|------------------------|---------------------------------------|------------------------------------------------------|
| **Campaign**<br>（广告系列） | 定义广告目标，例如提升应用安装、网站访问或品牌知名度。           | 这是广告的最高战略层级，决定了整个广告活动的总体方向和目标。                       |
| **Ad Squad**<br>（广告组）  | 设置具体投放策略：包括预算、出价、排期、目标受众、广告版位等。       | 在此层级进行广告优化和对比测试。你可以在一个系列下创建多个广告组，以测试不同受众、出价策略或创意的效果。 |
| **Ad**<br>（广告）         | 上传广告创意素材本身，如图片、视频，并填写广告文案、标题、行动号召按钮等。 | 这是与用户直接交互的展示层面。可以在一个广告组下放置多个广告创意，以测试不同素材的吸引力。        |

Organization
└── Ad Account
    └── Campaign（目标：APP_INSTALL）
        ├── Ad Squad 1（定位：美国18-25岁iOS用户）
        │   ├── Ad 1（视频创意A）
        │   └── Ad 2（视频创意B）
        └── Ad Squad 2（定位：英国18-25岁Android用户）
            ├── Ad 3（视频创意A）
            └── Ad 4（视频创意C）

### 账号概念
一、Organization（组织）
Organization 是 Snapchat 广告体系的最高层级，相当于"企业主体"，通常对应一家公司或集团。
二、Ad Account（广告账户）
Ad Account 是预算和结算的独立单元，每个 Ad Account 有单独的付款方式和账单。
三、Public Profile（公开档案）
Public Profile 是品牌在 Snapchat 的"永久主页"，用于有机增长和社区互动，与广告系统平行但可关联。

Organization: "ABC集团"
│
├── Ad Account 1: "ABC-美国电商"
│   ├── Campaign: 夏季促销
│   │   └── Ad Squad: 18-30岁女性
│   │       └── Ad: 视频广告A
│   └── Public Profile: "@ABC美国官方" (账号A)
│       ├── Saved Stories: 产品介绍
│       └── Spotlight视频: 用户测评
│
├── Ad Account 2: "ABC-欧洲B2B"
│   ├── Campaign: 企业解决方案
│   └── Public Profile: "@ABC欧洲企业" (账号B)
│
└── Ad Account 3: "代理商-客户X" (代理模式)
    ├── Campaign: 应用推广
    └── Public Profile: "@客户X官方" (客户自有)