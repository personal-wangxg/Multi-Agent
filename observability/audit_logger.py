from flask import Blueprint, request, jsonify
import json
import os
import uuid
from datetime import datetime
import structlog

audit_logger_bp = Blueprint('audit_logger', __name__)

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

logger = structlog.get_logger()

class AuditLogger:
    def __init__(self):
        self.logs = []
    
    def log(self, level, source, category, message, details=None):
        log_entry = {
            'log_id': str(uuid.uuid4())[:8],
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': level,
            'source': source,
            'category': category,
            'message': message,
            'details': details or {},
            'error': None
        }
        
        self.logs.append(log_entry)
        
        log_file = os.path.join(LOG_DIR, f"audit_{datetime.utcnow().strftime('%Y%m%d')}.json")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        return log_entry
    
    def info(self, source, category, message, details=None):
        return self.log('INFO', source, category, message, details)
    
    def warn(self, source, category, message, details=None):
        return self.log('WARN', source, category, message, details)
    
    def error(self, source, category, message, error=None, details=None):
        log_entry = self.log('ERROR', source, category, message, details)
        log_entry['error'] = {
            'type': type(error).__name__ if error else None,
            'message': str(error) if error else None
        }
        return log_entry

audit_logger = AuditLogger()

class TokenBudgetManager:
    def __init__(self):
        self.budgets = {}
    
    def create_budget(self, session_id, total_budget):
        self.budgets[session_id] = {
            'session_id': session_id,
            'total_budget': total_budget,
            'used_tokens': 0,
            'remaining_tokens': total_budget,
            'warning_threshold': 0.8,
            'critical_threshold': 0.95,
            'consumption_log': []
        }
        return self.budgets[session_id]
    
    def consume_tokens(self, session_id, tokens, agent_id, reason):
        if session_id not in self.budgets:
            return {'success': False, 'error': '预算不存在'}
        
        budget = self.budgets[session_id]
        budget['used_tokens'] += tokens
        budget['remaining_tokens'] = budget['total_budget'] - budget['used_tokens']
        budget['consumption_log'].append({
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'agent_id': agent_id,
            'tokens_used': tokens,
            'reason': reason
        })
        
        usage_ratio = budget['used_tokens'] / budget['total_budget']
        status = 'normal'
        
        if usage_ratio >= budget['critical_threshold']:
            status = 'critical'
            audit_logger.warn('token_budget', 'token', 'Token预算即将耗尽', {
                'session_id': session_id,
                'used_tokens': budget['used_tokens'],
                'total_budget': budget['total_budget'],
                'remaining_tokens': budget['remaining_tokens']
            })
        elif usage_ratio >= budget['warning_threshold']:
            status = 'warning'
            audit_logger.warn('token_budget', 'token', 'Token预算警告', {
                'session_id': session_id,
                'used_tokens': budget['used_tokens'],
                'total_budget': budget['total_budget']
            })
        
        return {
            'success': True,
            'status': status,
            'used_tokens': budget['used_tokens'],
            'remaining_tokens': budget['remaining_tokens'],
            'can_continue': usage_ratio < budget['critical_threshold']
        }
    
    def get_budget(self, session_id):
        return self.budgets.get(session_id, None)

token_budget_manager = TokenBudgetManager()

@audit_logger_bp.route('/logs', methods=['GET'])
def get_logs():
    level = request.args.get('level')
    source = request.args.get('source')
    category = request.args.get('category')
    
    filtered_logs = audit_logger.logs
    
    if level:
        filtered_logs = [l for l in filtered_logs if l['level'] == level]
    if source:
        filtered_logs = [l for l in filtered_logs if source.lower() in l['source'].lower()]
    if category:
        filtered_logs = [l for l in filtered_logs if category.lower() in l['category'].lower()]
    
    return jsonify({'logs': filtered_logs[-50:]})

@audit_logger_bp.route('/logs', methods=['POST'])
def add_log():
    data = request.json
    level = data.get('level', 'INFO')
    source = data.get('source')
    category = data.get('category')
    message = data.get('message')
    details = data.get('details')
    
    if level == 'ERROR':
        log_entry = audit_logger.error(source, category, message, details=details)
    elif level == 'WARN':
        log_entry = audit_logger.warn(source, category, message, details=details)
    else:
        log_entry = audit_logger.info(source, category, message, details=details)
    
    return jsonify({'log_id': log_entry['log_id']})

@audit_logger_bp.route('/token-budget/<session_id>', methods=['POST'])
def create_token_budget(session_id):
    data = request.json
    total_budget = data.get('total_budget', 100000)
    
    budget = token_budget_manager.create_budget(session_id, total_budget)
    return jsonify(budget)

@audit_logger_bp.route('/token-budget/<session_id>/consume', methods=['POST'])
def consume_tokens(session_id):
    data = request.json
    tokens = data.get('tokens', 0)
    agent_id = data.get('agent_id')
    reason = data.get('reason', 'unknown')
    
    result = token_budget_manager.consume_tokens(session_id, tokens, agent_id, reason)
    return jsonify(result)

@audit_logger_bp.route('/token-budget/<session_id>', methods=['GET'])
def get_token_budget(session_id):
    budget = token_budget_manager.get_budget(session_id)
    if not budget:
        return jsonify({'error': '预算不存在'}), 404
    return jsonify(budget)

@audit_logger_bp.route('/metrics', methods=['GET'])
def get_metrics():
    metrics = {
        'total_logs': len(audit_logger.logs),
        'info_logs': sum(1 for l in audit_logger.logs if l['level'] == 'INFO'),
        'warn_logs': sum(1 for l in audit_logger.logs if l['level'] == 'WARN'),
        'error_logs': sum(1 for l in audit_logger.logs if l['level'] == 'ERROR'),
        'active_budgets': len(token_budget_manager.budgets),
        'total_tokens_used': sum(b['used_tokens'] for b in token_budget_manager.budgets.values())
    }
    return jsonify(metrics)
