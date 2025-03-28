"""
WebSocket Authentication Service

Service for token-based authentication of WebSocket connections.
"""

import jwt
import time
import uuid
import logging
from datetime import datetime, timedelta
from flask import current_app, request
from functools import wraps

logger = logging.getLogger('websocket_auth')

class WebSocketAuthService:
    """Service for WebSocket authentication using JWT tokens."""
    
    def __init__(self, secret_key=None, token_expiry=3600, algorithm='HS256'):
        """
        Initialize the WebSocket auth service.
        
        Args:
            secret_key (str, optional): Secret key for signing tokens
            token_expiry (int): Token expiry time in seconds (default: 1 hour)
            algorithm (str): JWT algorithm to use
        """
        self._secret_key = secret_key
        self._token_expiry = token_expiry
        self._algorithm = algorithm
        self._initialized = False
        self.blacklisted_tokens = set()  # In a real app, use Redis or DB
    
    def _lazy_init(self):
        """Lazily initialize the service when within app context."""
        if not self._initialized:
            # This will only be accessed within an app context
            self.secret_key = self._secret_key or current_app.config.get('SECRET_KEY', 'websocket-secret-key')
            self.token_expiry = self._token_expiry
            self.algorithm = self._algorithm
            self._initialized = True
            logger.info("WebSocket Authentication Service initialized")
        
    def generate_token(self, user_id, permissions=None, custom_claims=None):
        """
        Generate a JWT token for WebSocket authentication.
        
        Args:
            user_id (int): User ID
            permissions (list, optional): List of permission strings
            custom_claims (dict, optional): Additional custom claims
            
        Returns:
            str: JWT token
        """
        self._lazy_init()
        
        now = datetime.utcnow()
        
        # Base claims
        claims = {
            'sub': str(user_id),
            'iat': now,
            'exp': now + timedelta(seconds=self.token_expiry),
            'jti': str(uuid.uuid4()),
            'scope': 'websocket',
        }
        
        # Add permissions
        if permissions:
            claims['permissions'] = permissions
            
        # Add custom claims
        if custom_claims:
            claims.update(custom_claims)
            
        # Generate token
        token = jwt.encode(claims, self.secret_key, algorithm=self.algorithm)
        logger.debug(f"Generated WebSocket token for user {user_id}")
        return token
        
    def verify_token(self, token):
        """
        Verify a WebSocket authentication token.
        
        Args:
            token (str): JWT token
            
        Returns:
            dict: Token claims if valid, None otherwise
        """
        self._lazy_init()
        
        try:
            # Check if token is blacklisted
            if token in self.blacklisted_tokens:
                logger.warning(f"Token {token[:10]}... is blacklisted")
                return None
                
            # Decode and verify token
            claims = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={'verify_signature': True}
            )
            
            # Additional verification
            if claims.get('scope') != 'websocket':
                logger.warning(f"Token {token[:10]}... has invalid scope: {claims.get('scope')}")
                return None
                
            return claims
        except jwt.ExpiredSignatureError:
            logger.warning(f"Token {token[:10]}... has expired")
            return None
        except jwt.PyJWTError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            return None
            
    def blacklist_token(self, token):
        """
        Blacklist a token.
        
        Args:
            token (str): JWT token
        """
        self._lazy_init()
        self.blacklisted_tokens.add(token)
        logger.info(f"Blacklisted token {token[:10]}...")
        
    def extract_token_from_request(self, req):
        """
        Extract token from request.
        
        Args:
            req: Flask request object
            
        Returns:
            str: Token or None
        """
        self._lazy_init()
        
        # Check for token in query parameters
        token = req.args.get('token')
        
        # Check for token in headers
        if not token and 'Authorization' in req.headers:
            auth_header = req.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                
        return token
        
    def authenticate_socket(self, req):
        """
        Authenticate a socket connection request.
        
        Args:
            req: Flask request object
            
        Returns:
            dict: User data if authenticated, None otherwise
        """
        self._lazy_init()
        
        # Extract token from socket request
        token = self.extract_token_from_request(req)
        
        if not token:
            logger.debug("No token found in request")
            return None
            
        # Verify token
        claims = self.verify_token(token)
        
        if not claims:
            return None
            
        # Return user data
        user_data = {
            'user_id': int(claims['sub']),
            'permissions': claims.get('permissions', []),
            'exp': claims['exp']
        }
        
        logger.debug(f"Socket authenticated for user {user_data['user_id']}")
        return user_data

# Create singleton instance
websocket_auth = WebSocketAuthService()