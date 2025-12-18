# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
"""
LLM Remote Service - 三阶段代码生成
"""
import os
from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


class LLMRemote:
    """Interface to LLM API for 3-stage code generation"""

    def __init__(self):
        """Initialize LLM client"""
        api_key = os.getenv('OPENAI_API_KEY')
        api_base = os.getenv('API_BASE', 'https://api.deepseek.com/v1')

        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        # Initialize ChatOpenAI
        self.llm = ChatOpenAI(
            model='deepseek-chat',
            base_url=api_base,
            temperature=0.3,
            max_tokens=6000
        )

    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate code using LLM API"""
        messages = []

        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        messages.append(HumanMessage(content=prompt))

        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            raise Exception(f"LLM API call failed: {str(e)}")

    def generate_stage1_code(
            self,
            platform: str,
            api_info: Dict,
            mock_auth: bool,
            step1_prompt: Optional[str]
    ) -> str:
        """
        Stage 1: 生成基础API函数

        基于API文档和step1提示生成:
        - create_campaign
        - create_ad_squad
        - create_media
        - upload_media
        - create_creative
        - create_ad
        """
        system_prompt = """你是一个专业的Python API客户端生成专家。

你的任务是根据API文档生成基础的API调用函数。

要求:
1. 生成独立的函数，每个函数对应一个API端点
2. 使用 requests 库进行HTTP调用
3. 函数签名使用 **kwargs 模式以支持灵活参数
4. 包含完整的类型提示和文档字符串
5. 实现适当的错误处理
6. 返回ONLY Python代码，不要有任何解释文字
7. 不要使用markdown代码块标记
"""

        # Build user prompt
        base_url = api_info.get('base_url', f'https://api.{platform}.com/v1')
        hierarchy = api_info.get('hierarchy', ['campaign', 'ad_squad', 'ad'])

        user_prompt = f"""平台: {platform.upper()}
Base URL: {base_url}
实体层级: {' -> '.join(hierarchy)}
模式: {'MOCK' if mock_auth else 'PRODUCTION'}

"""

        if step1_prompt:
            user_prompt += f"""参考示例代码:
{step1_prompt}

"""

        if mock_auth:
            user_prompt += f"""请生成MOCK模式的API函数:

必需函数:
1. create_campaign(account_id: str, **kwargs) -> Dict
2. create_{hierarchy[1]}(campaign_id: str, account_id: str, **kwargs) -> Dict
3. create_media(account_id: str, **kwargs) -> Dict
4. upload_media(media_id: str, **kwargs) -> Dict
5. create_creative(account_id: str, **kwargs) -> Dict
6. create_ad({hierarchy[1]}_id: str, account_id: str, **kwargs) -> Dict

要求:
- 所有函数返回mock数据，不进行真实API调用
- 生成mock ID使用格式: f"{{resource}}_mock_{{random.randint(10000, 99999)}}"
- 包含必要的导入: import random, from typing import Dict, Any
- 每个函数包含完整的docstring

生成代码:
"""
        else:
            user_prompt += f"""请生成PRODUCTION模式的API函数:

基于以下API端点:
"""
            for ep in api_info.get('endpoints', [])[:10]:
                user_prompt += f"- {ep.get('method', 'POST')} {ep.get('path', '')}\n"

            user_prompt += f"""
必需函数:
1. create_campaign(account_id: str, **kwargs) -> Dict
   - URL: {base_url}/adaccounts/{{account_id}}/campaigns
   - Method: POST
   
2. create_{hierarchy[1]}(campaign_id: str, account_id: str, **kwargs) -> Dict
   - URL: {base_url}/campaigns/{{campaign_id}}/{hierarchy[1]}s
   - Method: POST
   
3. create_media(account_id: str, **kwargs) -> Dict
   - URL: {base_url}/adaccounts/{{account_id}}/media
   - Method: POST
   
4. upload_media(media_id: str, **kwargs) -> Dict
   - URL: {base_url}/media/{{media_id}}/upload
   - Method: POST
   - 注意: 如果kwargs中有image_url，需要先下载图片
   
5. create_creative(account_id: str, **kwargs) -> Dict
   - URL: {base_url}/adaccounts/{{account_id}}/creatives
   - Method: POST
   
6. create_ad({hierarchy[1]}_id: str, account_id: str, **kwargs) -> Dict
   - URL: {base_url}/{hierarchy[1]}s/{{{hierarchy[1]}_id}}/ads
   - Method: POST

要求:
- 使用requests库
- 从环境变量读取token: os.getenv('{platform.upper()}_ACCESS_TOKEN')
- 设置headers: Authorization: Bearer {{token}}, Content-Type: application/json
- 实现错误处理
- 返回解析后的JSON响应

生成代码:
"""

        print(f"  调用LLM生成Stage 1代码...")
        code = self.generate_code(user_prompt, system_prompt)
        return self._extract_code(code)

    def generate_stage2_code(
            self,
            platform: str,
            api_info: Dict,
            mock_auth: bool,
            step2_prompt: Optional[str],
            stage1_code: str
    ) -> str:
        """
        Stage 2: 生成launch_campaign orchestrator

        这个函数解析用户JSON并按顺序调用Stage 1的函数
        """
        system_prompt = """你是一个专业的工作流编排专家。

你的任务是生成一个launch_campaign函数，该函数:
1. 接收用户的完整JSON数据
2. 解析为多个部分
3. 按正确顺序调用已有的API函数
4. 处理错误并返回完整结果

要求:
1. 使用已生成的函数(不要重新定义它们)
2. 实现完整的6步工作流
3. 处理部分失败的情况
4. 返回所有资源ID
5. 返回ONLY Python代码，不要有任何解释文字
6. 不要使用markdown代码块标记
"""

        hierarchy = api_info.get('hierarchy', ['campaign', 'ad_squad', 'ad'])

        user_prompt = f"""平台: {platform.upper()}
实体层级: {' -> '.join(hierarchy)}
模式: {'MOCK' if mock_auth else 'PRODUCTION'}

"""

        if step2_prompt:
            user_prompt += f"""工作流说明:
{step2_prompt}

"""

        user_prompt += f"""已有的API函数(Stage 1):
{stage1_code[:1000]}...

请生成launch_campaign函数:

def launch_campaign(
    account_id: str,
    campaign_data: Dict[str, Any],
    ad_squads_data: List[Dict[str, Any]],
    ads_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    \"\"\"
    完整的广告投放工作流
    
    步骤:
    1. 创建campaign
    2. 创建ad_squad(s)
    3. 对每个ad:
       - 创建media
       - 上传图片 (从image_url)
       - 创建creative
       - 创建ad
    
    返回:
    {{
        'status': 'success' or 'partial',
        'campaign_id': str,
        '{hierarchy[1]}_ids': List[str],
        'media_ids': List[str],
        'creative_ids': List[str],
        'ad_ids': List[str],
        'errors': List[str]
    }}
    \"\"\"
    # 实现代码

要求:
1. 使用已定义的create_campaign, create_{hierarchy[1]}, create_media等函数
2. 正确解析campaign_data, ad_squads_data, ads_data
3. 按顺序执行6个步骤
4. 处理image_url: 如果ads_data中有image_url，用于create_media和upload_media
5. 错误处理: 使用try-except，部分失败返回status='partial'
6. 包含详细的日志输出 (print语句)

生成代码:
"""

        print(f"  调用LLM生成Stage 2代码...")
        code = self.generate_code(user_prompt, system_prompt)
        return self._extract_code(code)

    def generate_stage3_code(
            self,
            platform: str,
            stage1_code: str,
            stage2_code: str,
            mock_auth: bool
    ) -> str:
        """
        Stage 3: 整合并检查语法

        合并Stage 1和Stage 2的代码，检查语法，添加必要的导入
        """
        system_prompt = """你是一个代码整合和质量检查专家。

你的任务是:
1. 整合两段代码
2. 检查语法错误
3. 添加缺失的导入
4. 添加必要的常量和辅助函数
5. 确保代码可以直接运行

要求:
1. 返回完整可运行的Python模块
2. 包含所有必要的导入
3. 修复任何语法错误
4. 添加模块级常量 (HIERARCHY, BASE_URL等)
5. 返回ONLY Python代码，不要有任何解释文字
6. 不要使用markdown代码块标记
"""

        user_prompt = f"""平台: {platform.upper()}
模式: {'MOCK' if mock_auth else 'PRODUCTION'}

Stage 1 代码 (基础API函数):
```python
{stage1_code}
```

Stage 2 代码 (launch_campaign orchestrator):
```python
{stage2_code}
```

请整合以上代码并:
1. 添加所有必要的导入 (os, requests, random, typing等)
2. 添加常量定义 (HIERARCHY, BASE_URL, ACCESS_TOKEN等)
3. 检查并修复语法错误
4. 确保函数之间没有重复定义
5. 确保launch_campaign可以正确调用Stage 1的函数
6. 添加模块级文档字符串

生成完整的、可运行的Python模块:
"""

        print(f"  调用LLM整合代码...")
        code = self.generate_code(user_prompt, system_prompt)
        return self._extract_code(code)

    def _extract_code(self, text: str) -> str:
        """Extract Python code from response"""
        import re

        # Try to find code block
        pattern = r'```(?:python)?\s*\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            return max(matches, key=len)

        # If no code block, return as is
        return text
