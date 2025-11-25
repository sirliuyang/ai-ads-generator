# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
"""
Flask API Server
Dynamically imports and uses generated API clients
"""
import os
import sys
import importlib.util
from flask import Flask, request, jsonify

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.flask_api.config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Cache for loaded API clients
_loaded_clients = {}


def load_api_client(platform: str):
    """
    Dynamically load generated API client for platform

    Args:
        platform: Platform name (e.g., 'snapchat')

    Returns:
        Loaded module or None if not found
    """
    if platform in _loaded_clients:
        return _loaded_clients[platform]

    # Build path to generated client
    client_file = os.path.join(
        app.config['GENERATED_CLIENTS_DIR'],
        f"{platform}_api.py"
    )

    if not os.path.exists(client_file):
        return None

    # Load module dynamically
    spec = importlib.util.spec_from_file_location(f"{platform}_api", client_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Cache it
    _loaded_clients[platform] = module

    return module


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Ads Generator API'
    })


@app.route('/api/platforms', methods=['GET'])
def list_platforms():
    """List available platform clients"""
    clients_dir = app.config['GENERATED_CLIENTS_DIR']

    if not os.path.exists(clients_dir):
        return jsonify({'platforms': []})

    platforms = []
    for file in os.listdir(clients_dir):
        if file.endswith('_api.py') and not file.startswith('__'):
            platform = file.replace('_api.py', '')
            platforms.append(platform)

    return jsonify({'platforms': platforms})


@app.route('/api/launch-campaign', methods=['POST'])
def launch_campaign():
    """
    Launch an ad campaign on specified platform

    Expected JSON body:
    {
        "platform": "snapchat",
        "account_id": "act_123",
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
                "headline": "50% Off!",
                "image_url": "https://example.com/img.jpg"
            }
        ]
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data or 'platform' not in data:
            return jsonify({
                'error': 'Missing required field: platform'
            }), 400

        platform = data['platform'].lower()

        # Load API client
        client_module = load_api_client(platform)
        if not client_module:
            return jsonify({
                'error': f'API client not found for platform: {platform}',
                'hint': f'Generate it first: python src/main.py --platform {platform} --docs <url>'
            }), 404

        # Instantiate the client class
        client_class = getattr(client_module, f'{platform.title()}AdsClient', None)
        if not client_class:
            return jsonify({
                'error': f'Client class not found in {platform}_api'
            }), 500

        client = client_class()

        # Extract data
        account_id = data.get('account_id', 'test_account')
        campaign_data = data.get('campaign', {})
        ad_squads_data = data.get('ad_squads', [])
        ads_data = data.get('ads', [])

        # Get hierarchy from client (or use defaults)
        hierarchy = getattr(client, 'HIERARCHY', ['campaign', 'ad_squad', 'ad'])

        result = {
            'status': 'success',
            'platform': platform,
            'campaign_id': None,
            f'{hierarchy[1]}_ids': [],
            'ad_ids': []
        }

        # === Step 1: Create campaign ===
        create_campaign = getattr(client, 'create_campaign', None)
        if not create_campaign:
            return jsonify({
                'error': f'create_campaign function not found in {platform}_api'
            }), 500

        # Prepare campaign parameters
        campaign_params = {
            'account_id': account_id,
            **campaign_data  # Spread all campaign data including 'name'
        }

        campaign = create_campaign(**campaign_params)
        result['campaign_id'] = campaign.get('id')

        # === Step 2: Create ad squads/groups (second level) ===
        create_second_level = getattr(client, f'create_{hierarchy[1]}', None)

        if create_second_level and ad_squads_data:
            for ad_squad_data in ad_squads_data:
                # Prepare ad squad parameters
                ad_squad_params = {
                    'campaign_id': campaign['id'],
                    'account_id': account_id,
                    **ad_squad_data  # Spread all ad squad data including 'name'
                }

                ad_squad = create_second_level(**ad_squad_params)
                result[f'{hierarchy[1]}_ids'].append(ad_squad.get('id'))

                # === Step 3: Create ads ===
                create_ad = getattr(client, 'create_ad', None)
                if create_ad and ads_data:
                    for ad_data in ads_data:
                        # Prepare ad parameters
                        ad_params = {
                            f'{hierarchy[1]}_id': ad_squad['id'],
                            'account_id': account_id,
                            **ad_data  # Spread all ad data including 'name'
                        }

                        ad = create_ad(**ad_params)
                        result['ad_ids'].append(ad.get('id'))

        return jsonify(result)

    except TypeError as e:
        return jsonify({
            'error': str(e),
            'type': 'TypeError',
            'hint': 'Check function signatures in generated client'
        }), 500
    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__
        }), 500


@app.route('/api/reload-client/<platform>', methods=['POST'])
def reload_client(platform):
    """Reload a specific platform client (useful after regenerating)"""
    platform = platform.lower()

    # Clear from cache
    if platform in _loaded_clients:
        del _loaded_clients[platform]

    # Try to load
    client = load_api_client(platform)

    if client:
        return jsonify({
            'status': 'success',
            'message': f'Reloaded {platform} client'
        })
    else:
        return jsonify({
            'error': f'Failed to load {platform} client'
        }), 404


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


def main():
    """Run Flask development server"""
    port = app.config['PORT']
    debug = app.config['DEBUG']

    print(f"\n{'=' * 60}")
    print(f"🚀 AI Ads Generator API Server")
    print(f"{'=' * 60}")
    print(f"Server: http://localhost:{port}")
    print(f"Health: http://localhost:{port}/health")
    print(f"Platforms: http://localhost:{port}/api/platforms")
    print(f"Launch Campaign: POST http://localhost:{port}/api/launch-campaign")
    print(f"{'=' * 60}\n")

    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    main()
