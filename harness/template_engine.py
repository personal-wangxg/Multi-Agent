from flask import Blueprint, request, jsonify
import yaml
import os
from jinja2 import Environment, BaseLoader

template_engine_bp = Blueprint('template_engine', __name__)

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')

def load_template(scene_type):
    template_path = os.path.join(TEMPLATE_DIR, f"{scene_type.lower()}_planner.yaml")
    if not os.path.exists(template_path):
        return None
    
    with open(template_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def inject_variables(template, variables):
    if not template:
        return None
    
    template_str = yaml.dump(template)
    env = Environment(loader=BaseLoader())
    template_obj = env.from_string(template_str)
    injected_str = template_obj.render(variables)
    return yaml.safe_load(injected_str)

def validate_template(template):
    required_fields = ['template_id', 'scene_type', 'agent_role', 'version', 
                       'role_definition', 'task_scope', 'output_format']
    missing_fields = [field for field in required_fields if field not in template]
    return {
        'valid': len(missing_fields) == 0,
        'missing_fields': missing_fields
    }

@template_engine_bp.route('/list', methods=['GET'])
def list_templates():
    templates = []
    for filename in os.listdir(TEMPLATE_DIR):
        if filename.endswith('.yaml'):
            template_path = os.path.join(TEMPLATE_DIR, filename)
            with open(template_path, 'r', encoding='utf-8') as f:
                template = yaml.safe_load(f)
                templates.append({
                    'template_id': template.get('template_id'),
                    'scene_type': template.get('scene_type'),
                    'agent_role': template.get('agent_role'),
                    'version': template.get('version')
                })
    return jsonify({'templates': templates})

@template_engine_bp.route('/<scene_type>', methods=['GET'])
def get_template(scene_type):
    template = load_template(scene_type)
    if not template:
        return jsonify({'error': f'Template not found for scene_type: {scene_type}'}), 404
    return jsonify(template)

@template_engine_bp.route('/<scene_type>/inject', methods=['POST'])
def inject_template_variables(scene_type):
    data = request.json
    variables = data.get('variables', {})
    
    template = load_template(scene_type)
    if not template:
        return jsonify({'error': f'Template not found for scene_type: {scene_type}'}), 404
    
    injected = inject_variables(template, variables)
    validation = validate_template(injected)
    
    return jsonify({
        'template_id': injected.get('template_id'),
        'injected_template': injected,
        'validation': validation
    })

@template_engine_bp.route('/validate', methods=['POST'])
def validate_template_endpoint():
    data = request.json
    template = data.get('template')
    validation = validate_template(template)
    return jsonify(validation)
