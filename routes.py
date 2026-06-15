from flask import jsonify, request

def register_routes(app):
    from harness.template_engine import template_engine_bp
    from harness.schema_validator import schema_validator_bp
    from harness.tool_whitelist import tool_whitelist_bp
    from memory.memory_manager import memory_manager_bp
    from observability.audit_logger import audit_logger_bp
    
    app.register_blueprint(template_engine_bp, url_prefix='/api/harness/templates')
    app.register_blueprint(schema_validator_bp, url_prefix='/api/harness/validation')
    app.register_blueprint(tool_whitelist_bp, url_prefix='/api/harness/whitelist')
    app.register_blueprint(memory_manager_bp, url_prefix='/api/memory')
    app.register_blueprint(audit_logger_bp, url_prefix='/api/observability')
    
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy', 'service': 'EduAgents Harness Layer'})
