from flask import Blueprint, request, jsonify
import json
import os
import uuid
from datetime import datetime

memory_manager_bp = Blueprint('memory_manager', __name__)

SESSION_DIR = os.path.join(os.path.dirname(__file__), '..', 'sessions')
LTM_DIR = os.path.join(os.path.dirname(__file__), '..', 'ltm')

os.makedirs(SESSION_DIR, exist_ok=True)
os.makedirs(LTM_DIR, exist_ok=True)

class ShortTermMemory:
    def __init__(self, session_id):
        self.session_id = session_id
        self.messages = []
        self.context = {}
        self.token_count = 0
        self.max_tokens = 8192
    
    def add_message(self, role, content):
        message = {
            'message_id': str(uuid.uuid4())[:8],
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        self.messages.append(message)
        self.token_count += len(content) // 4
        self._compress_if_needed()
        return message
    
    def _compress_if_needed(self):
        if self.token_count > self.max_tokens * 0.8:
            if len(self.messages) > 2:
                self.messages = [self.messages[0]] + self.messages[-2:]
                self.token_count = sum(len(m['content']) // 4 for m in self.messages)
    
    def get_summary(self):
        return {
            'session_id': self.session_id,
            'message_count': len(self.messages),
            'token_count': self.token_count,
            'max_tokens': self.max_tokens,
            'context': self.context
        }

class WorkingMemory:
    @staticmethod
    def write_file(session_id, path, content):
        session_path = os.path.join(SESSION_DIR, session_id)
        os.makedirs(session_path, exist_ok=True)
        full_path = os.path.join(session_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {'success': True, 'path': path}
    
    @staticmethod
    def read_file(session_id, path):
        full_path = os.path.join(SESSION_DIR, session_id, path)
        if not os.path.exists(full_path):
            return {'success': False, 'error': '文件不存在'}
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {'success': True, 'content': content}
    
    @staticmethod
    def list_files(session_id, directory=''):
        session_path = os.path.join(SESSION_DIR, session_id)
        full_path = os.path.join(session_path, directory)
        
        if not os.path.exists(full_path):
            return {'success': False, 'error': '目录不存在'}
        
        files = []
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            files.append({
                'name': item,
                'type': 'directory' if os.path.isdir(item_path) else 'file'
            })
        return {'success': True, 'files': files}

class LongTermMemory:
    @staticmethod
    def write_memory(memory_data):
        memory_id = memory_data.get('memory_id', str(uuid.uuid4())[:8])
        memory_data['memory_id'] = memory_id
        memory_data['created_at'] = datetime.utcnow().isoformat() + 'Z'
        memory_data['usage_count'] = 0
        
        memory_path = os.path.join(LTM_DIR, f"{memory_id}.json")
        with open(memory_path, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)
        
        return {'success': True, 'memory_id': memory_id}
    
    @staticmethod
    def read_memory(memory_id):
        memory_path = os.path.join(LTM_DIR, f"{memory_id}.json")
        if not os.path.exists(memory_path):
            return {'success': False, 'error': '记忆不存在'}
        
        with open(memory_path, 'r', encoding='utf-8') as f:
            memory_data = json.load(f)
        
        memory_data['usage_count'] += 1
        with open(memory_path, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)
        
        return {'success': True, 'memory': memory_data}
    
    @staticmethod
    def search_memories(query, limit=3):
        results = []
        for filename in os.listdir(LTM_DIR):
            if filename.endswith('.json'):
                memory_path = os.path.join(LTM_DIR, filename)
                with open(memory_path, 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
                
                content = memory_data.get('content', '')
                if query.lower() in content.lower():
                    results.append(memory_data)
        
        results.sort(key=lambda x: x.get('rating', 0), reverse=True)
        return {'success': True, 'memories': results[:limit]}

stm_store = {}

@memory_manager_bp.route('/stm/<session_id>/messages', methods=['POST'])
def add_stm_message(session_id):
    data = request.json
    role = data.get('role')
    content = data.get('content')
    
    if session_id not in stm_store:
        stm_store[session_id] = ShortTermMemory(session_id)
    
    message = stm_store[session_id].add_message(role, content)
    return jsonify({'message': message, 'summary': stm_store[session_id].get_summary()})

@memory_manager_bp.route('/stm/<session_id>', methods=['GET'])
def get_stm(session_id):
    if session_id not in stm_store:
        return jsonify({'error': '会话不存在'}), 404
    
    return jsonify(stm_store[session_id].get_summary())

@memory_manager_bp.route('/wm/<session_id>/files', methods=['POST'])
def wm_write_file(session_id):
    data = request.json
    path = data.get('path')
    content = data.get('content')
    
    result = WorkingMemory.write_file(session_id, path, content)
    return jsonify(result)

@memory_manager_bp.route('/wm/<session_id>/files/<path:file_path>', methods=['GET'])
def wm_read_file(session_id, file_path):
    result = WorkingMemory.read_file(session_id, file_path)
    if not result['success']:
        return jsonify(result), 404
    return jsonify(result)

@memory_manager_bp.route('/wm/<session_id>/files', methods=['GET'])
def wm_list_files(session_id):
    directory = request.args.get('directory', '')
    result = WorkingMemory.list_files(session_id, directory)
    return jsonify(result)

@memory_manager_bp.route('/ltm/memories', methods=['POST'])
def ltm_write_memory():
    data = request.json
    result = LongTermMemory.write_memory(data)
    return jsonify(result)

@memory_manager_bp.route('/ltm/memories/<memory_id>', methods=['GET'])
def ltm_read_memory(memory_id):
    result = LongTermMemory.read_memory(memory_id)
    if not result['success']:
        return jsonify(result), 404
    return jsonify(result)

@memory_manager_bp.route('/ltm/search', methods=['GET'])
def ltm_search():
    query = request.args.get('query', '')
    limit = int(request.args.get('limit', 3))
    result = LongTermMemory.search_memories(query, limit)
    return jsonify(result)

@memory_manager_bp.route('/ltm/memories', methods=['GET'])
def ltm_list_memories():
    memories = []
    for filename in os.listdir(LTM_DIR):
        if filename.endswith('.json'):
            memory_path = os.path.join(LTM_DIR, filename)
            with open(memory_path, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
                memories.append({
                    'memory_id': memory_data.get('memory_id'),
                    'type': memory_data.get('type'),
                    'domain': memory_data.get('domain'),
                    'rating': memory_data.get('rating'),
                    'usage_count': memory_data.get('usage_count')
                })
    return jsonify({'memories': memories})
