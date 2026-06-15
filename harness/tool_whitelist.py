from flask import Blueprint, request, jsonify
import yaml
import os
import re

tool_whitelist_bp = Blueprint('tool_whitelist', __name__)

WHITELIST_DIR = os.path.join(os.path.dirname(__file__), '..', 'whitelists')

os.makedirs(WHITELIST_DIR, exist_ok=True)

def load_whitelist(agent_id):
    whitelist_path = os.path.join(WHITELIST_DIR, f"{agent_id}.yaml")
    if not os.path.exists(whitelist_path):
        return None
    
    with open(whitelist_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def check_tool_permission(agent_id, tool_name, params):
    whitelist = load_whitelist(agent_id)
    if not whitelist:
        return {'allowed': False, 'reason': '白名单配置不存在'}
    
    allowed_tools = whitelist.get('tool_whitelist', {}).get('allowed_tools', [])
    denied_tools = whitelist.get('tool_whitelist', {}).get('denied_tools', [])
    
    for denied in denied_tools:
        if denied.get('name') == tool_name:
            return {'allowed': False, 'reason': denied.get('reason', '工具在黑名单中')}
    
    for allowed in allowed_tools:
        if allowed.get('name') == tool_name:
            return validate_tool_params(allowed, params)
    
    return {'allowed': False, 'reason': '工具不在白名单中'}

def validate_tool_params(allowed_tool, params):
    param_constraints = allowed_tool.get('params', {})
    
    for param_name, constraints in param_constraints.items():
        if param_name in params:
            value = params[param_name]
            
            if 'type' in constraints:
                expected_type = constraints['type']
                actual_type = type(value).__name__
                if expected_type == 'string' and not isinstance(value, str):
                    return {'allowed': False, 'reason': f'参数 {param_name} 类型应为字符串'}
                if expected_type == 'integer' and not isinstance(value, int):
                    return {'allowed': False, 'reason': f'参数 {param_name} 类型应为整数'}
            
            if 'pattern' in constraints and isinstance(value, str):
                if not re.match(constraints['pattern'], value):
                    return {'allowed': False, 'reason': f'参数 {param_name} 不符合格式要求'}
            
            if 'max_length' in constraints and isinstance(value, str):
                if len(value) > constraints['max_length']:
                    return {'allowed': False, 'reason': f'参数 {param_name} 长度超出限制'}
    
    return {'allowed': True, 'reason': '工具调用已授权'}

@tool_whitelist_bp.route('/list', methods=['GET'])
def list_whitelists():
    whitelists = []
    for filename in os.listdir(WHITELIST_DIR):
        if filename.endswith('.yaml'):
            agent_id = filename.replace('.yaml', '')
            whitelist = load_whitelist(agent_id)
            if whitelist:
                whitelists.append({
                    'agent_id': agent_id,
                    'scene_type': whitelist.get('scene_type'),
                    'framework': whitelist.get('framework')
                })
    return jsonify({'whitelists': whitelists})

@tool_whitelist_bp.route('/<agent_id>', methods=['GET'])
def get_whitelist(agent_id):
    whitelist = load_whitelist(agent_id)
    if not whitelist:
        return jsonify({'error': f'白名单配置不存在: {agent_id}'}), 404
    return jsonify(whitelist)

@tool_whitelist_bp.route('/<agent_id>', methods=['POST'])
def create_whitelist(agent_id):
    data = request.json
    whitelist_path = os.path.join(WHITELIST_DIR, f"{agent_id}.yaml")
    
    with open(whitelist_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    
    return jsonify({'message': '白名单配置已创建', 'agent_id': agent_id})

@tool_whitelist_bp.route('/<agent_id>/check', methods=['POST'])
def check_permission(agent_id):
    data = request.json
    tool_name = data.get('tool_name')
    params = data.get('params', {})
    
    result = check_tool_permission(agent_id, tool_name, params)
    return jsonify(result)

@tool_whitelist_bp.route('/<agent_id>/allowed-tools', methods=['GET'])
def get_allowed_tools(agent_id):
    whitelist = load_whitelist(agent_id)
    if not whitelist:
        return jsonify({'error': f'白名单配置不存在: {agent_id}'}), 404
    
    allowed_tools = whitelist.get('tool_whitelist', {}).get('allowed_tools', [])
    return jsonify({'allowed_tools': allowed_tools})
