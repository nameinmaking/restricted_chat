from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///audit_logs.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    domain = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User', backref='account', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='account', lazy=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # owner, admin, analyst, content_creator
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.String(50))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='audit_logs')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def log_audit_action(action, resource_type, resource_id=None, details=None):
    """Helper function to log audit actions"""
    if current_user.is_authenticated:
        audit_log = AuditLog(
            user_id=current_user.id,
            account_id=current_user.account_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()

# Routes
@app.route('/')
def index():
    return jsonify({
        'message': 'Ecommerce Audit Logs API',
        'version': '1.0.0',
        'endpoints': {
            'accounts': '/api/accounts',
            'users': '/api/users',
            'audit_logs': '/api/audit-logs',
            'auth': '/api/auth'
        }
    })

@app.route('/audit-logs')
@login_required
def audit_logs_page():
    # Only owners and admins can view audit logs
    if current_user.role not in ['owner', 'admin']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    return render_template('audit_logs.html')

@app.route('/api/accounts', methods=['POST'])
def create_account():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['name', 'domain', 'owner_email', 'owner_password', 'owner_first_name', 'owner_last_name']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if account domain already exists
    if Account.query.filter_by(domain=data['domain']).first():
        return jsonify({'error': 'Account with this domain already exists'}), 409
    
    # Check if owner email already exists
    if User.query.filter_by(email=data['owner_email']).first():
        return jsonify({'error': 'User with this email already exists'}), 409
    
    # Create account
    account = Account(name=data['name'], domain=data['domain'])
    db.session.add(account)
    db.session.flush()  # Get the account ID
    
    # Create owner user
    owner = User(
        email=data['owner_email'],
        password_hash=generate_password_hash(data['owner_password']),
        first_name=data['owner_first_name'],
        last_name=data['owner_last_name'],
        role='owner',
        account_id=account.id
    )
    db.session.add(owner)
    db.session.commit()
    
    log_audit_action('account_created', 'account', str(account.id), f'Account {account.name} created')
    
    return jsonify({
        'message': 'Account created successfully',
        'account': {
            'id': account.id,
            'name': account.name,
            'domain': account.domain,
            'owner_id': owner.id
        }
    }), 201

@app.route('/api/users', methods=['POST'])
@login_required
def create_user():
    # Only owners and admins can create users
    if current_user.role not in ['owner', 'admin']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    data = request.get_json()
    
    if not data or not all(k in data for k in ['email', 'password', 'first_name', 'last_name', 'role']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate role
    valid_roles = ['admin', 'analyst', 'content_creator']
    if data['role'] not in valid_roles:
        return jsonify({'error': 'Invalid role'}), 400
    
    # Check if user email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'User with this email already exists'}), 409
    
    # Create user
    user = User(
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        first_name=data['first_name'],
        last_name=data['last_name'],
        role=data['role'],
        account_id=current_user.account_id
    )
    db.session.add(user)
    db.session.commit()
    
    log_audit_action('user_created', 'user', str(user.id), f'User {user.email} created with role {user.role}')
    
    return jsonify({
        'message': 'User created successfully',
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user and check_password_hash(user.password_hash, data['password']) and user.is_active:
        login_user(user)
        log_audit_action('user_login', 'user', str(user.id), 'User logged in successfully')
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'account_id': user.account_id
            }
        })
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    log_audit_action('user_logout', 'user', str(current_user.id), 'User logged out')
    logout_user()
    return jsonify({'message': 'Logout successful'})

@app.route('/api/audit-logs', methods=['GET'])
@login_required
def get_audit_logs():
    # Only owners and admins can view audit logs
    if current_user.role not in ['owner', 'admin']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    # Get query parameters for filtering
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 100)
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action')
    resource_type = request.args.get('resource_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query
    query = AuditLog.query.filter_by(account_id=current_user.account_id)
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if action:
        query = query.filter(AuditLog.action.contains(action))
    if resource_type:
        query = query.filter_by(resource_type=resource_type)
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    # Order by created_at descending
    query = query.order_by(AuditLog.created_at.desc())
    
    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    audit_logs = pagination.items
    
    # Format response
    logs = []
    for log in audit_logs:
        logs.append({
            'id': log.id,
            'user': {
                'id': log.user.id,
                'email': log.user.email,
                'first_name': log.user.first_name,
                'last_name': log.user.last_name,
                'role': log.user.role
            },
            'action': log.action,
            'resource_type': log.resource_type,
            'resource_id': log.resource_id,
            'details': log.details,
            'ip_address': log.ip_address,
            'user_agent': log.user_agent,
            'created_at': log.created_at.isoformat()
        })
    
    return jsonify({
        'audit_logs': logs,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    # Only owners and admins can view users
    if current_user.role not in ['owner', 'admin']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    users = User.query.filter_by(account_id=current_user.account_id).all()
    
    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat()
        })
    
    return jsonify({'users': user_list})

@app.route('/api/accounts/<int:account_id>', methods=['GET'])
@login_required
def get_account(account_id):
    # Users can only view their own account
    if current_user.account_id != account_id:
        return jsonify({'error': 'Access denied'}), 403
    
    account = Account.query.get_or_404(account_id)
    
    return jsonify({
        'account': {
            'id': account.id,
            'name': account.name,
            'domain': account.domain,
            'created_at': account.created_at.isoformat()
        }
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 