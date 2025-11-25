# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
"""
LLM Remote Service
Handles communication with DeepSeek API via LangChain
"""
import os
from typing import Dict, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


class LLMRemote:
    """Interface to DeepSeek API for code generation"""

    def __init__(self):
        """Initialize LLM client"""
        api_key = os.getenv('OPENAI_API_KEY')
        api_base = os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1')

        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        # Initialize ChatOpenAI with DeepSeek endpoint
        self.llm = ChatOpenAI(
            model='deepseek-chat',
            base_url=api_base,
            temperature=0.3,
            max_tokens=4000
        )

    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate code using DeepSeek API

        Args:
            prompt: User prompt describing what to generate
            system_prompt: Optional system prompt for context

        Returns:
            Generated code as string
        """
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        # Add user prompt
        messages.append(HumanMessage(content=prompt))

        try:
            # Call LLM
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            raise Exception(f"LLM API call failed: {str(e)}")

    def generate_api_client_code(
            self,
            platform: str,
            api_info: Dict,
            mock_auth: bool = False
    ) -> str:
        """
        Generate complete API client code for a platform

        Args:
            platform: Platform name
            api_info: Parsed API information
            mock_auth: Whether to generate mock or real API client

        Returns:
            Complete Python module code
        """
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(platform, api_info, mock_auth)

        print(f"Generating {'mock' if mock_auth else 'production'} API client code...")
        code = self.generate_code(user_prompt, system_prompt)

        # Extract code from markdown if present
        code = self._extract_code_from_markdown(code)

        return code

    def _build_system_prompt(self) -> str:
        """Build system prompt for code generation"""
        return """You are an expert Python developer specializing in API client generation.
Your task is to generate clean, production-ready Python code for advertising platform API clients.

Requirements:
1. Generate a complete Python module with all necessary imports
2. Include proper error handling and type hints
3. Follow PEP 8 style guidelines
4. Add clear docstrings for all functions
5. Return ONLY the Python code, no explanations or markdown
6. Code should be ready to save as a .py file and run immediately
"""

    def _build_user_prompt(self, platform: str, api_info: Dict, mock_auth: bool) -> str:
        """Build user prompt with API information"""

        hierarchy = api_info.get('hierarchy', ['campaign', 'ad_group', 'ad'])
        auth_type = api_info['authentication'].get('type', 'oauth2')

        if mock_auth:
            prompt = f"""Generate a MOCK Python API client for {platform.upper()} advertising platform.

Platform: {platform}
Entity Hierarchy: {' -> '.join(hierarchy)}
Auth Type: {auth_type} (MOCKED - no real authentication)

Required Functions (all should return MOCK data):
"""
            for i, entity in enumerate(hierarchy):
                parent = hierarchy[i - 1] if i > 0 else None
                parent_param = f"{parent}_id, " if parent else ""

                prompt += f"""
- create_{entity}({parent_param}name, **kwargs):
  Should return mock {entity} dict with 'id', 'name', and 'status' fields
"""

            prompt += f"""
Additional Requirements:
1. NO real API calls - all functions return mock data immediately
2. Generate realistic mock IDs (use random or incremental IDs)
3. Include a MockAPIClient class or use module-level functions
4. Mock responses should include: id (string), name (string), status ('ACTIVE')
5. Accept **kwargs for flexibility but ignore them in mock mode
6. Add environment variable {platform.upper()}_ACCESS_TOKEN (optional, can be None in mock)
7. Include proper docstrings explaining this is MOCK data

Example mock return:
{{
    'id': '{entity[:3]}_mock_' + str(random.randint(1000, 9999)),
    'name': name,
    'status': 'ACTIVE'
}}

Generate the complete Python module now:"""

        else:  # Production mode
            endpoints_str = "\n".join([
                f"  - {ep.get('method', 'POST')} {ep.get('path', '')}"
                for ep in api_info.get('endpoints', [])[:10]
            ])

            prompt = f"""Generate a PRODUCTION-READY Python API client for {platform.upper()} advertising platform.

Platform: {platform}
Entity Hierarchy: {' -> '.join(hierarchy)}
Auth Type: {auth_type}

Available Endpoints:
{endpoints_str if endpoints_str else '  (Use standard REST patterns)'}

Required Functions:
"""
            for i, entity in enumerate(hierarchy):
                parent = hierarchy[i - 1] if i > 0 else None
                parent_param = f"{parent}_id, " if parent else ""

                prompt += f"""
- create_{entity}({parent_param}account_id, name, **kwargs):
  Makes real API call to create {entity}
  Returns: dict with id, name, status from API response
"""

            prompt += f"""
Additional Requirements:
1. Use requests library for HTTP calls
2. Read access token from environment: {platform.upper()}_ACCESS_TOKEN
3. Implement proper OAuth2 Bearer authentication
4. Base URL should follow {platform} API conventions (e.g., https://adsapi.snapchat.com)
5. Include error handling for HTTP errors
6. Add retry logic for transient failures (optional but recommended)
7. Parse JSON responses and return Python dicts
8. Use proper HTTP methods (POST for create)
9. Set Content-Type: application/json headers
10. Include comprehensive docstrings

API Documentation Context:
{api_info.get('raw_text', '')[:1000]}

Generate the complete, production-ready Python module now:"""

        return prompt

    def _extract_code_from_markdown(self, text: str) -> str:
        """Extract Python code from markdown code blocks"""
        import re

        # Try to find code block
        pattern = r'```(?:python)?\s*\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            # Return the largest code block
            return max(matches, key=len)

        # If no code block found, return as is
        return text
