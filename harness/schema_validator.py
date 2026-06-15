from flask import Blueprint, request, jsonify
import json
import os
import jsonschema
from jsonschema import validate

schema_validator_bp = Blueprint('schema_validator', __name__)

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), '..', 'schemas')

def load_schema(schema_id):
    schema_path = os.path.join(SCHEMA_DIR, f"{schema_id}.json")
    if not os.path.exists(schema_path):
        return None
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_schema(output, schema):
    try:
        validate(instance=output, schema=schema)
        return {
            'success': True,
            'errors': [],
            'stage': 'schema'
        }
    except jsonschema.ValidationError as e:
        return {
            'success': False,
            'errors': [{
                'field': list(e.path)[0] if e.path else 'unknown',
                'error_type': 'schema_violation',
                'message': e.message,
                'expected': str(e.schema) if e.schema else None,
                'actual': str(e.instance)
            }],
            'stage': 'schema'
        }

def filter_content(output, prohibited_topics):
    errors = []
    output_str = json.dumps(output, ensure_ascii=False)
    
    for topic in prohibited_topics:
        if topic in output_str:
            errors.append({
                'field': 'content',
                'error_type': 'prohibited_topic',
                'message': f'内容包含禁止话题: {topic}',
                'expected': '不包含禁止话题',
                'actual': topic
            })
    
    return {
        'success': len(errors) == 0,
        'errors': errors,
        'stage': 'content'
    }

def check_task_completeness(output, todo_items):
    errors = []
    covered_items = []
    
    if 'chapters' in output:
        covered_items.append('拆解章节结构')
    
    if 'total_periods' in output:
        covered_items.append('分析课程目标')
    
    for item in todo_items:
        if item['label'] not in covered_items and item.get('required', False):
            errors.append({
                'field': 'completeness',
                'error_type': 'missing_required_task',
                'message': f'未完成必需任务: {item["label"]}',
                'expected': item['label'],
                'actual': '未完成'
            })
    
    return {
        'success': len(errors) == 0,
        'errors': errors,
        'stage': 'completeness'
    }

def run_validation_pipeline(output, harness_config):
    results = []
    
    schema_id = harness_config.get('schema_ref')
    if schema_id:
        schema = load_schema(schema_id)
        if schema:
            schema_result = validate_schema(output, schema)
            results.append(schema_result)
            if not schema_result['success']:
                return {
                    'overall_success': False,
                    'results': results,
                    'retry_count': 0,
                    'max_retries': harness_config.get('max_retries', 3)
                }
    
    prohibited_topics = harness_config.get('prohibited_topics', [])
    content_result = filter_content(output, prohibited_topics)
    results.append(content_result)
    if not content_result['success']:
        return {
            'overall_success': False,
            'results': results,
            'retry_count': 0,
            'max_retries': harness_config.get('max_retries', 3)
        }
    
    todo_items = harness_config.get('todo_template', [])
    completeness_result = check_task_completeness(output, todo_items)
    results.append(completeness_result)
    
    return {
        'overall_success': all(r['success'] for r in results),
        'results': results,
        'retry_count': 0,
        'max_retries': harness_config.get('max_retries', 3)
    }

@schema_validator_bp.route('/schemas', methods=['GET'])
def list_schemas():
    schemas = []
    for filename in os.listdir(SCHEMA_DIR):
        if filename.endswith('.json'):
            schema_name = filename.replace('.json', '')
            schemas.append({'schema_id': schema_name})
    return jsonify({'schemas': schemas})

@schema_validator_bp.route('/schema/<schema_id>', methods=['GET'])
def get_schema(schema_id):
    schema = load_schema(schema_id)
    if not schema:
        return jsonify({'error': f'Schema not found: {schema_id}'}), 404
    return jsonify(schema)

@schema_validator_bp.route('/validate/schema', methods=['POST'])
def validate_schema_endpoint():
    data = request.json
    output = data.get('output')
    schema_id = data.get('schema_id')
    
    schema = load_schema(schema_id)
    if not schema:
        return jsonify({'error': f'Schema not found: {schema_id}'}), 404
    
    result = validate_schema(output, schema)
    return jsonify(result)

@schema_validator_bp.route('/validate/content', methods=['POST'])
def validate_content_endpoint():
    data = request.json
    output = data.get('output')
    prohibited_topics = data.get('prohibited_topics', [])
    
    result = filter_content(output, prohibited_topics)
    return jsonify(result)

@schema_validator_bp.route('/validate/completeness', methods=['POST'])
def validate_completeness_endpoint():
    data = request.json
    output = data.get('output')
    todo_items = data.get('todo_items', [])
    
    result = check_task_completeness(output, todo_items)
    return jsonify(result)

@schema_validator_bp.route('/validate/pipeline', methods=['POST'])
def validate_pipeline_endpoint():
    data = request.json
    output = data.get('output')
    harness_config = data.get('harness_config', {})
    
    result = run_validation_pipeline(output, harness_config)
    return jsonify(result)
