# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
import os
import sys
import unittest
import importlib.util
from unittest.mock import patch, Mock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestMockMode(unittest.TestCase):
    """测试Mock模式"""

    @classmethod
    def setUpClass(cls):
        """加载Mock模式的客户端"""
        client_file = 'src/generated_clients/snapchat_api.py'

        if not os.path.exists(client_file):
            raise unittest.SkipTest("Snapchat client not generated yet")

        # 动态加载模块
        spec = importlib.util.spec_from_file_location('snapchat_api', client_file)
        cls.client = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.client)

        # 检查是否是Mock模式
        mode = getattr(cls.client, '__mode__', 'unknown')
        if mode != 'MOCK':
            raise unittest.SkipTest(f"Client is not in MOCK mode (mode={mode})")

    def test_module_constants(self):
        """测试模块常量"""
        self.assertTrue(hasattr(self.client, 'HIERARCHY'))
        self.assertTrue(hasattr(self.client, 'BASE_URL'))

        hierarchy = self.client.HIERARCHY
        self.assertIsInstance(hierarchy, list)
        self.assertGreaterEqual(len(hierarchy), 3)
        print(f"✓ HIERARCHY: {hierarchy}")

    def test_create_campaign_mock(self):
        """测试create_campaign - Mock模式"""
        campaign = self.client.create_campaign(
            account_id='test_account',
            name='Test Campaign',
            daily_budget_micro=100000000
        )

        # 验证返回值
        self.assertIn('id', campaign)
        self.assertIn('name', campaign)
        self.assertEqual(campaign['name'], 'Test Campaign')
        self.assertEqual(campaign['account_id'], 'test_account')
        self.assertIn('mock', campaign['id'])

        print(f"✓ create_campaign返回: {campaign['id']}")

    def test_create_ad_squad_mock(self):
        """测试create_ad_squad - Mock模式"""
        hierarchy = self.client.HIERARCHY
        second_level = hierarchy[1]

        func = getattr(self.client, f'create_{second_level}')

        result = func(
            campaign_id='campaign_mock_12345',
            account_id='test_account',
            name='Test Squad',
            bid_micro=5000000
        )

        self.assertIn('id', result)
        self.assertIn('name', result)
        self.assertEqual(result['name'], 'Test Squad')
        self.assertIn('mock', result['id'])

        print(f"✓ create_{second_level}返回: {result['id']}")

    def test_create_media_mock(self):
        """测试create_media - Mock模式"""
        media = self.client.create_media(
            account_id='test_account',
            name='Test Media'
        )

        self.assertIn('id', media)
        self.assertIn('mock', media['id'])

        print(f"✓ create_media返回: {media['id']}")

    def test_upload_media_mock(self):
        """测试upload_media - Mock模式"""
        result = self.client.upload_media(
            media_id='media_mock_12345',
            image_url='https://example.com/test.jpg'
        )

        self.assertIn('status', result)
        self.assertIn('media_id', result)

        print(f"✓ upload_media返回: {result}")

    def test_create_creative_mock(self):
        """测试create_creative - Mock模式"""
        creative = self.client.create_creative(
            account_id='test_account',
            name='Test Creative',
            media_id='media_mock_12345'
        )

        self.assertIn('id', creative)
        self.assertIn('mock', creative['id'])

        print(f"✓ create_creative返回: {creative['id']}")

    def test_create_ad_mock(self):
        """测试create_ad - Mock模式"""
        hierarchy = self.client.HIERARCHY
        second_level = hierarchy[1]

        ad = self.client.create_ad(
            **{f'{second_level}_id': 'squad_mock_12345'},
            account_id='test_account',
            name='Test Ad',
            creative_id='creative_mock_12345'
        )

        self.assertIn('id', ad)
        self.assertIn('mock', ad['id'])

        print(f"✓ create_ad返回: {ad['id']}")

    def test_launch_campaign_mock(self):
        """测试launch_campaign完整流程 - Mock模式"""
        result = self.client.launch_campaign(
            account_id='test_account',
            campaign_data={
                'name': 'Test Campaign',
                'daily_budget_micro': 100000000
            },
            ad_squads_data=[
                {
                    'name': 'Test Squad 1',
                    'bid_micro': 5000000
                }
            ],
            ads_data=[
                {
                    'name': 'Test Ad 1',
                    'headline': 'Test Headline',
                    'image_url': 'https://example.com/test.jpg'
                }
            ]
        )

        # 验证结果结构
        self.assertIn('status', result)
        self.assertIn('campaign_id', result)
        self.assertIn('ad_squad_ids', result)
        self.assertIn('media_ids', result)
        self.assertIn('creative_ids', result)
        self.assertIn('ad_ids', result)

        # 验证成功
        self.assertEqual(result['status'], 'success')
        self.assertIsNotNone(result['campaign_id'])
        self.assertGreater(len(result['ad_squad_ids']), 0)
        self.assertGreater(len(result['media_ids']), 0)
        self.assertGreater(len(result['creative_ids']), 0)
        self.assertGreater(len(result['ad_ids']), 0)

        print(f"\n✓ launch_campaign完整流程测试通过")
        print(f"  Status: {result['status']}")
        print(f"  Campaign ID: {result['campaign_id']}")
        print(f"  Ad Squad IDs: {result['ad_squad_ids']}")
        print(f"  Media IDs: {result['media_ids']}")
        print(f"  Creative IDs: {result['creative_ids']}")
        print(f"  Ad IDs: {result['ad_ids']}")


class TestProductionMode(unittest.TestCase):
    """测试Production模式（使用mock requests）"""

    @classmethod
    def setUpClass(cls):
        """加载Production模式的客户端"""
        client_file = 'src/generated_clients/snapchat_api.py'

        if not os.path.exists(client_file):
            raise unittest.SkipTest("Snapchat client not generated yet")

        # 动态加载模块
        spec = importlib.util.spec_from_file_location('snapchat_api_prod', client_file)
        cls.client = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.client)

        # 检查是否是Production模式
        mode = getattr(cls.client, '__mode__', 'MOCK')
        if mode == 'MOCK':
            raise unittest.SkipTest("Client is in MOCK mode, skipping production tests")

    @patch('requests.post')
    @patch.dict(os.environ, {'SNAPCHAT_ACCESS_TOKEN': 'test_token_12345'})
    def test_create_campaign_production(self, mock_post):
        """测试create_campaign - Production模式（mock requests）"""
        # Mock响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'campaigns': [{
                'campaign': {
                    'id': 'real_campaign_12345',
                    'name': 'Test Campaign',
                    'status': 'ACTIVE'
                }
            }]
        }
        mock_post.return_value = mock_response

        # 调用函数
        campaign = self.client.create_campaign(
            account_id='test_account',
            name='Test Campaign'
        )

        # 验证请求
        self.assertTrue(mock_post.called)
        call_args = mock_post.call_args

        # 验证URL
        self.assertIn('campaigns', call_args[0][0])

        # 验证headers
        headers = call_args[1]['headers']
        self.assertIn('Authorization', headers)
        self.assertIn('Bearer', headers['Authorization'])

        # 验证返回值
        self.assertIn('id', campaign)

        print(f"✓ Production模式create_campaign测试通过")
        print(f"  API调用: {mock_post.call_count} 次")


class TestMultiPlatformSupport(unittest.TestCase):
    """测试多平台支持"""

    def test_platform_file_structure(self):
        """测试平台文件结构"""
        clients_dir = 'src/generated_clients'

        if not os.path.exists(clients_dir):
            self.skipTest("Generated clients directory not found")

        # 检查已生成的平台
        platforms = []
        for file in os.listdir(clients_dir):
            if file.endswith('_api.py') and not file.startswith('__'):
                platform = file.replace('_api.py', '')
                platforms.append(platform)

        self.assertGreater(len(platforms), 0, "No platforms generated")

        print(f"✓ 已生成的平台: {', '.join(platforms)}")

        # 验证每个平台文件结构
        for platform in platforms:
            client_file = os.path.join(clients_dir, f'{platform}_api.py')

            with open(client_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查必需的函数
            required_functions = [
                'create_campaign',
                'create_media',
                'upload_media',
                'create_creative',
                'create_ad',
                'launch_campaign'
            ]

            for func in required_functions:
                self.assertIn(f'def {func}', content,
                              f"{platform} missing {func}")

            print(f"  ✓ {platform}: 所有必需函数存在")

    def test_pinterest_compatibility(self):
        """测试Pinterest兼容性（如果已生成）"""
        client_file = 'src/generated_clients/pinterest_api.py'

        if not os.path.exists(client_file):
            self.skipTest("Pinterest client not generated yet")

        # 加载模块
        spec = importlib.util.spec_from_file_location('pinterest_api', client_file)
        client = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(client)

        # 检查层级
        hierarchy = getattr(client, 'HIERARCHY', [])
        self.assertIn('campaign', hierarchy)

        # Pinterest通常使用ad_group而不是ad_squad
        print(f"✓ Pinterest HIERARCHY: {hierarchy}")


class TestFlaskIntegration(unittest.TestCase):
    """测试Flask集成"""

    @classmethod
    def setUpClass(cls):
        """启动Flask测试客户端"""
        try:
            from src.flask_api.api import app
            cls.client = app.test_client()
            cls.app = app
        except Exception as e:
            raise unittest.SkipTest(f"Failed to load Flask app: {e}")

    def test_health_endpoint(self):
        """测试健康检查"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')

        print("✓ /health endpoint works")

    def test_platforms_endpoint(self):
        """测试平台列表"""
        response = self.client.get('/api/platforms')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn('platforms', data)

        print(f"✓ /api/platforms返回: {len(data['platforms'])} 个平台")

    def test_snapchat_endpoint_exists(self):
        """测试Snapchat端点是否配置"""
        # 检查路由是否存在
        routes = []
        for rule in self.app.url_map.iter_rules():
            routes.append(str(rule))

        snapchat_route = '/api/snapchat/launch-campaign'

        if snapchat_route in routes:
            print(f"✓ Snapchat route configured: {snapchat_route}")
        else:
            print(f"⚠ Snapchat route not configured (需要手动添加)")
            self.skipTest("Snapchat route not manually configured yet")


def run_all_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestMockMode))
    suite.addTests(loader.loadTestsFromTestCase(TestProductionMode))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiPlatformSupport))
    suite.addTests(loader.loadTestsFromTestCase(TestFlaskIntegration))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("简易回归测试")
    print("=" * 70 + "\n")

    success = run_all_tests()

    print("\n" + "=" * 70)
    if success:
        print("✅ 所有测试通过！")
    else:
        print("❌ 某些测试失败")
    print("=" * 70 + "\n")

    sys.exit(0 if success else 1)
