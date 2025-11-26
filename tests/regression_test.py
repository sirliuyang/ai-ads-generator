# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
"""
Regression Test Suite
Orchestrates complete testing workflow:
1. Generate API client (test_agent.py)
2. Test generated client (test_clients.py)
3. Test Flask integration
"""
import os
import sys
import unittest
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class RegressionTestSuite:
    """Complete regression test suite"""

    def __init__(self):
        self.results = {
            'start_time': datetime.now(),
            'end_time': None,
            'steps': [],
            'overall_success': False
        }
        self.test_platform = 'snapchat'
        self.test_docs_url = 'https://developers.snap.com/api/marketing-api/Ads-API/ads'
        self.output_dir = 'src/generated_clients'

    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70 + "\n")

    def print_step(self, step_num, total_steps, description):
        """Print step information"""
        print(f"\n[Step {step_num}/{total_steps}] {description}")
        print("-" * 70)

    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        self.print_header("Checking Prerequisites")

        checks = []

        # Check OPENAI_API_KEY
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            print("✓ OPENAI_API_KEY found")
            checks.append(True)
        else:
            print("✗ OPENAI_API_KEY not found")
            print("  Set OPENAI_API_KEY in .env file")
            checks.append(False)

        # Check required directories
        dirs = ['src', 'src/service', 'src/flask_api', 'tests']
        for directory in dirs:
            if os.path.exists(directory):
                print(f"✓ Directory exists: {directory}")
                checks.append(True)
            else:
                print(f"✗ Directory missing: {directory}")
                checks.append(False)

        # Check required files
        files = [
            'src/service/code_agent.py',
            'src/service/llm_remote.py',
            'src/service/platform_doc_parser.py',
            'src/flask_api/api.py',
            'tests/test_agent.py',
            'tests/test_clients.py'
        ]
        for file in files:
            if os.path.exists(file):
                print(f"✓ File exists: {file}")
                checks.append(True)
            else:
                print(f"✗ File missing: {file}")
                checks.append(False)

        all_passed = all(checks)
        if all_passed:
            print("\n✅ All prerequisites met")
        else:
            print("\n❌ Some prerequisites missing")

        return all_passed

    def step_1_generate_client(self):
        """Step 1: Generate API client"""
        self.print_step(1, 5, "Generate Snapchat Mock Client")

        try:
            # Import and use code agent
            from src.service.code_agent import CodeAgent

            agent = CodeAgent()

            print(f"Platform: {self.test_platform}")
            print(f"Docs URL: {self.test_docs_url}")
            print(f"Mode: Mock (--mock-auth)")
            print(f"Output: {self.output_dir}\n")

            output_file = agent.generate_api_client(
                platform=self.test_platform,
                docs_url=self.test_docs_url,
                mock_auth=True,
                output_dir=self.output_dir
            )

            print(f"\n✓ Client generated: {output_file}")

            # Verify file exists and has content
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    content = f.read()
                print(f"✓ File size: {len(content)} characters")

                # Check for key functions
                required = ['create_campaign', 'HIERARCHY']
                for func in required:
                    if func in content:
                        print(f"✓ Found: {func}")

                self.results['steps'].append({
                    'step': 1,
                    'name': 'Generate Client',
                    'status': 'success',
                    'output_file': output_file
                })
                return True
            else:
                print(f"✗ Generated file not found: {output_file}")
                self.results['steps'].append({
                    'step': 1,
                    'name': 'Generate Client',
                    'status': 'failed',
                    'error': 'File not found'
                })
                return False

        except Exception as e:
            print(f"\n✗ Generation failed: {e}")
            import traceback
            traceback.print_exc()

            self.results['steps'].append({
                'step': 1,
                'name': 'Generate Client',
                'status': 'failed',
                'error': str(e)
            })
            return False

    def step_2_test_agent(self):
        """Step 2: Run agent tests"""
        self.print_step(2, 5, "Run Agent Tests (test_agent.py)")

        try:
            # Import test_agent
            from tests import test_agent

            # Run specific tests that don't require long API calls
            suite = unittest.TestSuite()

            # Add quick tests
            suite.addTest(test_agent.TestPlatformDocParser('test_extract_endpoints'))
            suite.addTest(test_agent.TestPlatformDocParser('test_extract_auth_info'))
            suite.addTest(test_agent.TestPlatformDocParser('test_extract_hierarchy'))

            if os.getenv('OPENAI_API_KEY'):
                suite.addTest(test_agent.TestLLMRemote('test_load_custom_workflow'))

            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)

            success = result.wasSuccessful()

            if success:
                print("\n✓ Agent tests passed")
            else:
                print("\n⚠ Some agent tests failed")

            self.results['steps'].append({
                'step': 2,
                'name': 'Agent Tests',
                'status': 'success' if success else 'failed',
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors)
            })

            return success

        except Exception as e:
            print(f"\n✗ Agent tests failed: {e}")
            self.results['steps'].append({
                'step': 2,
                'name': 'Agent Tests',
                'status': 'failed',
                'error': str(e)
            })
            return False

    def step_3_test_generated_client(self):
        """Step 3: Test generated client directly"""
        self.print_step(3, 5, "Test Generated Client Directly")

        try:
            client_file = os.path.join(self.output_dir, f'{self.test_platform}_api.py')

            if not os.path.exists(client_file):
                print(f"✗ Client file not found: {client_file}")
                self.results['steps'].append({
                    'step': 3,
                    'name': 'Test Generated Client',
                    'status': 'failed',
                    'error': 'Client file not found'
                })
                return False

            # Import the client
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                f'{self.test_platform}_api',
                client_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            print(f"✓ Client imported successfully")

            # Test basic functions
            tests_passed = []

            # Test create_campaign
            if hasattr(module, 'create_campaign'):
                campaign = module.create_campaign(
                    account_id='test',
                    name='Test Campaign'
                )
                if campaign and 'id' in campaign:
                    print(f"✓ create_campaign works: {campaign['id']}")
                    tests_passed.append(True)
                else:
                    print(f"✗ create_campaign returned invalid data")
                    tests_passed.append(False)

            # Test orchestrator if available
            if hasattr(module, 'launch_campaign'):
                print("\n✓ Orchestrator function found")
                result = module.launch_campaign(
                    account_id='test',
                    campaign_data={'name': 'Test'},
                    ad_squads_data=[{'name': 'Squad'}],
                    ads_data=[{'name': 'Ad'}]
                )

                if result and result.get('status') == 'success':
                    print(f"✓ Orchestrator works")
                    print(f"  Campaign: {result.get('campaign_id')}")
                    print(f"  Ads: {len(result.get('ad_ids', []))}")
                    tests_passed.append(True)
                else:
                    print(f"✗ Orchestrator failed")
                    tests_passed.append(False)

            success = all(tests_passed) if tests_passed else False

            self.results['steps'].append({
                'step': 3,
                'name': 'Test Generated Client',
                'status': 'success' if success else 'failed',
                'tests_passed': sum(tests_passed),
                'tests_total': len(tests_passed)
            })

            return success

        except Exception as e:
            print(f"\n✗ Client test failed: {e}")
            import traceback
            traceback.print_exc()

            self.results['steps'].append({
                'step': 3,
                'name': 'Test Generated Client',
                'status': 'failed',
                'error': str(e)
            })
            return False

    def step_4_test_client_suite(self):
        """Step 4: Run client test suite"""
        self.print_step(4, 5, "Run Client Test Suite (test_clients.py)")

        try:
            from tests import test_clients

            # Run client tests
            suite = unittest.TestSuite()

            # Add tests
            suite.addTest(test_clients.TestGeneratedClients('test_snapchat_mock_client'))
            suite.addTest(test_clients.TestFlaskAPIIntegration('test_health_endpoint'))
            suite.addTest(test_clients.TestFlaskAPIIntegration('test_list_platforms'))

            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)

            success = result.wasSuccessful()

            if success:
                print("\n✓ Client tests passed")
            else:
                print("\n⚠ Some client tests failed")

            self.results['steps'].append({
                'step': 4,
                'name': 'Client Test Suite',
                'status': 'success' if success else 'failed',
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors)
            })

            return success

        except Exception as e:
            print(f"\n✗ Client tests failed: {e}")
            self.results['steps'].append({
                'step': 4,
                'name': 'Client Test Suite',
                'status': 'failed',
                'error': str(e)
            })
            return False

    def step_5_test_flask_integration(self):
        """Step 5: Test Flask API integration"""
        self.print_step(5, 5, "Test Flask API Integration")

        try:
            from tests import test_clients

            # Run Flask integration tests
            suite = unittest.TestSuite()
            suite.addTest(test_clients.TestFlaskAPIIntegration('test_launch_campaign_snapchat_mock'))

            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)

            success = result.wasSuccessful()

            if success:
                print("\n✓ Flask integration tests passed")
            else:
                print("\n⚠ Some Flask tests failed")

            self.results['steps'].append({
                'step': 5,
                'name': 'Flask Integration',
                'status': 'success' if success else 'failed',
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors)
            })

            return success

        except Exception as e:
            print(f"\n✗ Flask integration tests failed: {e}")
            self.results['steps'].append({
                'step': 5,
                'name': 'Flask Integration',
                'status': 'failed',
                'error': str(e)
            })
            return False

    def print_summary(self):
        """Print test summary"""
        self.results['end_time'] = datetime.now()
        duration = (self.results['end_time'] - self.results['start_time']).total_seconds()

        self.print_header("Regression Test Summary")

        print(f"Start Time: {self.results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End Time: {self.results['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {duration:.2f} seconds\n")

        print("Steps:")
        for step in self.results['steps']:
            status_icon = "✓" if step['status'] == 'success' else "✗"
            print(f"  {status_icon} Step {step['step']}: {step['name']} - {step['status']}")
            if 'tests_run' in step:
                print(f"    Tests: {step['tests_run']}, Failures: {step.get('failures', 0)}")
            if 'error' in step:
                print(f"    Error: {step['error']}")

        print("\nOverall Result:")
        if self.results['overall_success']:
            print("  ✅ ALL TESTS PASSED")
        else:
            print("  ❌ SOME TESTS FAILED")

        print("\n" + "=" * 70 + "\n")

    def run(self):
        """Run complete regression test suite"""
        self.print_header("AI Ads Generator - Regression Test Suite")

        print(f"Platform: {self.test_platform}")
        print(f"Mode: Mock (Testing)")
        print(f"Timestamp: {self.results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")

        # Check prerequisites
        if not self.check_prerequisites():
            print("\n❌ Prerequisites not met. Aborting.")
            self.results['overall_success'] = False
            self.print_summary()
            return False

        # Run all steps
        steps = [
            self.step_1_generate_client,
            self.step_2_test_agent,
            self.step_3_test_generated_client,
            self.step_4_test_client_suite,
            self.step_5_test_flask_integration
        ]

        results = []
        for step_func in steps:
            result = step_func()
            results.append(result)

            if not result:
                print(f"\n⚠ Step failed, but continuing with remaining tests...")

        # Overall success if all critical steps passed
        # Step 1 (generation) is critical
        critical_passed = results[0] if results else False
        all_passed = all(results)

        self.results['overall_success'] = all_passed

        # Print summary
        self.print_summary()

        return all_passed


def main():
    """Main entry point"""
    suite = RegressionTestSuite()
    success = suite.run()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
