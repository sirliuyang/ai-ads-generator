# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
"""
Flask API Server - 简化版
只作为入口，手动配置生成的API客户端路由

使用方法:
1. 生成平台客户端: python src/main.py --platform snapchat --docs <url>
2. 在下方手动添加路由配置
3. 启动服务器: python src/flask_api/api.py
"""
import os
import sys
from flask import Flask, request, jsonify

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.flask_api.config import Config

app = Flask(__name__)
app.config.from_object(Config)


# ============================================================================
# 核心端点
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Ads Generator API'
    })


@app.route('/api/platforms', methods=['GET'])
def list_platforms():
    """列出已配置的平台"""
    # 手动维护的平台列表
    configured_platforms = []

    # 自动检测generated_clients目录
    clients_dir = app.config['GENERATED_CLIENTS_DIR']
    if os.path.exists(clients_dir):
        for file in os.listdir(clients_dir):
            if file.endswith('_api.py') and not file.startswith('__'):
                platform = file.replace('_api.py', '')
                configured_platforms.append({
                    'name': platform,
                    'file': file,
                    'status': 'generated'
                })

    return jsonify({'platforms': configured_platforms})


# ============================================================================
# 平台特定路由 - 手动配置区域
# ============================================================================

# ------------------------------
# Snapchat 配置
# ------------------------------
try:
    from src.generated_clients.snapchat_api import launch_campaign as snapchat_launch


    @app.route('/api/launch-campaign', methods=['POST'])
    def snapchat_launch_campaign():
        """
        Snapchat 广告投放

        POST /api/snapchat/launch-campaign
        {
          "account_id": "...",
          "campaign": {...},
          "ad_squads": [{...}],
          "ads": [{...}]
        }
        """
        try:
            data = request.get_json()

            # 验证必需字段
            required_fields = ['account_id', 'campaign', 'ad_squads', 'ads']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # 调用生成的API
            result = snapchat_launch(
                account_id=data['account_id'],
                campaign_data=data['campaign'],
                ad_squads_data=data['ad_squads'],
                ads_data=data['ads']
            )

            return jsonify(result)

        except Exception as e:
            return jsonify({
                'error': str(e),
                'type': type(e).__name__
            }), 500


    print("✓ Snapchat routes configured")

except ImportError as e:
    print(f"⚠ Snapchat client not available: {e}")
    print("  Generate it first: python src/main.py --platform snapchat --docs <url>")


# ------------------------------
# Pinterest 配置 (示例)
# ------------------------------
# try:
#     from src.generated_clients.pinterest_api import launch_campaign as pinterest_launch
#
#     @app.route('/api/pinterest/launch-campaign', methods=['POST'])
#     def pinterest_launch_campaign():
#         """Pinterest 广告投放"""
#         try:
#             data = request.get_json()
#             result = pinterest_launch(
#                 account_id=data['account_id'],
#                 campaign_data=data['campaign'],
#                 ad_squads_data=data.get('ad_groups', []),  # Pinterest uses ad_groups
#                 ads_data=data['ads']
#             )
#             return jsonify(result)
#         except Exception as e:
#             return jsonify({'error': str(e)}), 500
#
#     print("✓ Pinterest routes configured")
# except ImportError:
#     print("⚠ Pinterest client not available")


# ============================================================================
# 添加更多平台配置的位置
# ============================================================================

# 提示:
# 1. 生成客户端后，在上方添加 import 语句
# 2. 复制路由模板，修改平台名称
# 3. 重启Flask服务器


# ============================================================================
# 错误处理
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# 服务器启动
# ============================================================================

def main():
    """启动Flask服务器"""
    port = app.config['PORT']
    debug = app.config['DEBUG']

    print(f"\n{'=' * 70}")
    print(f"🚀 AI Ads Generator API Server")
    print(f"{'=' * 70}")
    print(f"Server: http://localhost:{port}")
    print(f"Health: http://localhost:{port}/health")
    print(f"Platforms: http://localhost:{port}/api/platforms")
    print(f"\nConfigured endpoints:")

    # 列出所有配置的路由
    for rule in app.url_map.iter_rules():
        if rule.endpoint not in ['static', 'health_check', 'list_platforms']:
            methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
            print(f"  {methods:6} {rule.rule}")

    print(f"{'=' * 70}")
    print(f"\n手动配置说明:")
    print(f"1. 生成平台客户端")
    print(f"2. 编辑 src/flask_api/api.py")
    print(f"3. 添加import和路由配置")
    print(f"4. 重启服务器")
    print(f"{'=' * 70}\n")

    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    main()
