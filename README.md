# Ecommerce Audit Logs System

A Flask-based audit logging system for ecommerce companies similar to Shopify. This application provides comprehensive audit trails for user actions within multi-tenant accounts, with role-based access control and secure authentication.

## Features

- **Multi-tenant Architecture**: Support for multiple accounts/organizations
- **Role-based Access Control**: Owner, Admin, Analyst, and Content Creator roles
- **Comprehensive Audit Logging**: Track all user actions with detailed metadata
- **Secure Authentication**: Password hashing and session management
- **RESTful API**: Clean API endpoints for all operations
- **Search and Filtering**: Advanced audit log search capabilities
- **Database Support**: SQLAlchemy with support for SQLite, PostgreSQL, MySQL

## Database Schema

### Account
- `id`: Primary key
- `name`: Account/organization name
- `domain`: Unique domain identifier
- `created_at`: Account creation timestamp

### User
- `id`: Primary key
- `email`: Unique email address
- `password_hash`: Hashed password
- `first_name`, `last_name`: User details
- `role`: User role (owner, admin, analyst, content_creator)
- `account_id`: Foreign key to Account
- `is_active`: Account status
- `created_at`: User creation timestamp

### AuditLog
- `id`: Primary key
- `user_id`: User who performed the action
- `account_id`: Account context
- `action`: Action performed (e.g., "user_login", "product_created")
- `resource_type`: Type of resource affected
- `resource_id`: ID of the affected resource
- `details`: Additional details about the action
- `ip_address`: IP address of the user
- `user_agent`: Browser/client information
- `created_at`: Timestamp of the action

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///audit_logs.db
FLASK_ENV=development
FLASK_DEBUG=1
```

### 3. Initialize Database

```bash
python init_db.py
```

This will:
- Create all database tables
- Optionally create sample data for testing

### 4. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## API Endpoints

### Authentication

#### POST /api/auth/login
Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "owner",
    "account_id": 1
  }
}
```

#### POST /api/auth/logout
Logout the current user.

### Account Management

#### POST /api/accounts
Create a new account with an owner user.

**Request:**
```json
{
  "name": "My Ecommerce Store",
  "domain": "my-store.com",
  "owner_email": "owner@my-store.com",
  "owner_password": "securepassword",
  "owner_first_name": "John",
  "owner_last_name": "Owner"
}
```

#### GET /api/accounts/{account_id}
Get account details (requires authentication).

### User Management

#### POST /api/users
Create a new user (requires owner/admin role).

**Request:**
```json
{
  "email": "admin@my-store.com",
  "password": "password123",
  "first_name": "Jane",
  "last_name": "Admin",
  "role": "admin"
}
```

#### GET /api/users
Get all users in the account (requires owner/admin role).

### Audit Logs

#### GET /api/audit-logs
Get audit logs with filtering and pagination (requires owner/admin role).

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 50, max: 100)
- `user_id`: Filter by user ID
- `action`: Filter by action type
- `resource_type`: Filter by resource type
- `start_date`: Filter by start date (ISO format)
- `end_date`: Filter by end date (ISO format)

**Response:**
```json
{
  "audit_logs": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "owner"
      },
      "action": "user_login",
      "resource_type": "user",
      "resource_id": "1",
      "details": "User logged in successfully",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 100,
    "pages": 2,
    "has_next": true,
    "has_prev": false
  }
}
```

## Role Permissions

| Action | Owner | Admin | Analyst | Content Creator |
|--------|-------|-------|---------|-----------------|
| View Audit Logs | ✅ | ✅ | ❌ | ❌ |
| Create Users | ✅ | ✅ | ❌ | ❌ |
| View Users | ✅ | ✅ | ❌ | ❌ |
| View Account | ✅ | ✅ | ✅ | ✅ |

## Sample Data

When you run `init_db.py` with sample data, it creates:

- **Account**: "Sample Ecommerce Store" (domain: sample-store.com)
- **Users**:
  - Owner: `owner@sample-store.com` (password: `owner123`)
  - Admin: `admin@sample-store.com` (password: `admin123`)
  - Analyst: `analyst@sample-store.com` (password: `analyst123`)
  - Content Creator: `creator@sample-store.com` (password: `creator123`)
- **100 sample audit logs** with various actions and timestamps

## Usage Examples

### Creating an Account

```bash
curl -X POST http://localhost:5000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Store",
    "domain": "mystore.com",
    "owner_email": "owner@mystore.com",
    "owner_password": "password123",
    "owner_first_name": "John",
    "owner_last_name": "Owner"
  }'
```

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "owner@mystore.com",
    "password": "password123"
  }'
```

### View Audit Logs

```bash
curl -X GET "http://localhost:5000/api/audit-logs?page=1&per_page=10" \
  -H "Cookie: session=your-session-cookie"
```

## Security Features

- **Password Hashing**: All passwords are hashed using Werkzeug's security functions
- **Session Management**: Flask-Login handles secure session management
- **Role-based Access**: API endpoints are protected based on user roles
- **Audit Trail**: All actions are logged with user context and metadata
- **Input Validation**: All API inputs are validated before processing

## Future Enhancements

- **Chat Agent Integration**: AI-powered chat interface for querying audit data
- **Real-time Notifications**: WebSocket support for real-time audit log updates
- **Advanced Analytics**: Dashboard with charts and insights
- **Export Functionality**: CSV/PDF export of audit logs
- **API Rate Limiting**: Protect against abuse
- **Multi-factor Authentication**: Enhanced security for sensitive operations

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Database Migrations

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Code Style

This project follows PEP 8 style guidelines. Use a linter like `flake8` or `black` for code formatting.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
