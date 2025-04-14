# Autenticación y Autorización

Este documento describe los sistemas de autenticación y autorización implementados en AdFlux para garantizar un acceso seguro a la aplicación y sus recursos.

## Autenticación

AdFlux implementa un sistema de autenticación robusto basado en JWT (JSON Web Tokens) con soporte para autenticación de dos factores (2FA).

### Flujo de Autenticación

![Flujo de Autenticación](./diagramas/flujo-autenticacion.png)

1. El usuario envía sus credenciales (nombre de usuario/email y contraseña) al servidor.
2. El servidor verifica las credenciales contra la base de datos.
3. Si las credenciales son válidas, se verifica si el usuario tiene 2FA habilitado:
   - Si no tiene 2FA, se genera un token de acceso y un token de refresco.
   - Si tiene 2FA, se solicita un código de verificación adicional.
4. Una vez completada la autenticación, se devuelven los tokens al cliente.
5. El cliente almacena los tokens y los utiliza para autenticar solicitudes posteriores.

### JSON Web Tokens (JWT)

AdFlux utiliza dos tipos de tokens JWT:

1. **Token de Acceso**: Token de corta duración (1 hora) utilizado para autenticar solicitudes a la API.
2. **Token de Refresco**: Token de larga duración (30 días) utilizado para obtener nuevos tokens de acceso sin requerir credenciales.

Estructura de los tokens JWT:

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_id",
    "iat": 1516239022,
    "exp": 1516242622,
    "jti": "unique_token_id",
    "type": "access",
    "fresh": true,
    "csrf": "csrf_token",
    "roles": ["admin", "editor"]
  },
  "signature": "..."
}
```

### Autenticación de Dos Factores (2FA)

AdFlux soporta autenticación de dos factores basada en TOTP (Time-based One-Time Password) compatible con aplicaciones como Google Authenticator, Authy y Microsoft Authenticator.

Proceso de configuración de 2FA:

1. El usuario activa 2FA en su perfil.
2. El sistema genera una clave secreta y la muestra como un código QR.
3. El usuario escanea el código QR con su aplicación de autenticación.
4. El usuario introduce un código de verificación para confirmar la configuración.
5. El sistema genera códigos de respaldo para el usuario en caso de pérdida de acceso a su dispositivo.

### Gestión de Sesiones

AdFlux implementa las siguientes medidas para la gestión segura de sesiones:

- **Expiración de Tokens**: Los tokens de acceso expiran después de 1 hora de inactividad.
- **Renovación de Sesiones**: Los tokens de acceso pueden renovarse utilizando el token de refresco.
- **Revocación de Tokens**: Los tokens pueden ser revocados en caso de cierre de sesión o compromiso de seguridad.
- **Rotación de Tokens**: Los tokens de refresco se rotan periódicamente para limitar el impacto de una posible filtración.

### Protección contra Ataques

AdFlux implementa las siguientes medidas para proteger el sistema de autenticación:

- **Limitación de Tasa**: Límite de intentos de inicio de sesión (5 intentos en 15 minutos).
- **Tiempo de Espera Progresivo**: Aumento del tiempo de espera después de intentos fallidos.
- **Notificaciones de Inicio de Sesión**: Alertas por email para inicios de sesión desde nuevos dispositivos o ubicaciones.
- **Detección de Anomalías**: Monitorización de patrones de inicio de sesión inusuales.

## Autorización

AdFlux implementa un sistema de control de acceso basado en roles (RBAC) para gestionar los permisos de los usuarios.

### Roles y Permisos

AdFlux define los siguientes roles predeterminados:

1. **Admin**: Acceso completo a todas las funcionalidades.
2. **Manager**: Gestión de campañas, ofertas de trabajo y usuarios (sin acceso a configuración del sistema).
3. **Editor**: Creación y edición de campañas y ofertas de trabajo.
4. **Viewer**: Solo lectura de campañas, ofertas de trabajo y métricas.

Cada rol tiene asociado un conjunto de permisos específicos:

```python
ROLE_PERMISSIONS = {
    'admin': [
        'view_dashboard', 'view_campaigns', 'create_campaigns', 'edit_campaigns', 'delete_campaigns',
        'view_job_openings', 'create_job_openings', 'edit_job_openings', 'delete_job_openings',
        'view_candidates', 'create_candidates', 'edit_candidates', 'delete_candidates',
        'view_users', 'create_users', 'edit_users', 'delete_users',
        'view_settings', 'edit_settings', 'view_reports', 'export_data'
    ],
    'manager': [
        'view_dashboard', 'view_campaigns', 'create_campaigns', 'edit_campaigns', 'delete_campaigns',
        'view_job_openings', 'create_job_openings', 'edit_job_openings', 'delete_job_openings',
        'view_candidates', 'create_candidates', 'edit_candidates',
        'view_users', 'create_users', 'edit_users',
        'view_reports', 'export_data'
    ],
    'editor': [
        'view_dashboard', 'view_campaigns', 'create_campaigns', 'edit_campaigns',
        'view_job_openings', 'create_job_openings', 'edit_job_openings',
        'view_candidates', 'create_candidates', 'edit_candidates',
        'view_reports'
    ],
    'viewer': [
        'view_dashboard', 'view_campaigns', 'view_job_openings', 'view_candidates', 'view_reports'
    ]
}
```

### Implementación del RBAC

El sistema RBAC se implementa a través de los siguientes componentes:

1. **Modelos de Base de Datos**:

```python
class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    # Relaciones
    permissions = db.relationship('Permission', secondary='role_permissions', 
                                 backref=db.backref('roles', lazy='dynamic'))

class Permission(db.Model):
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

# Tabla de asociación para roles y permisos
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)

# Tabla de asociación para usuarios y roles
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)
```

2. **Decoradores para Proteger Rutas**:

```python
def permission_required(permission):
    """
    Decorador para verificar si el usuario tiene un permiso específico.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verificar autenticación
            verify_jwt_in_request()
            
            # Obtener ID de usuario del token
            user_id = get_jwt_identity()
            
            # Verificar si el usuario tiene el permiso
            if not has_permission(user_id, permission):
                return jsonify({"error": "Permiso denegado"}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def role_required(role):
    """
    Decorador para verificar si el usuario tiene un rol específico.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verificar autenticación
            verify_jwt_in_request()
            
            # Obtener ID de usuario del token
            user_id = get_jwt_identity()
            
            # Verificar si el usuario tiene el rol
            if not has_role(user_id, role):
                return jsonify({"error": "Permiso denegado"}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator
```

3. **Funciones de Utilidad**:

```python
def get_user_roles(user_id):
    """
    Obtiene los roles de un usuario.
    """
    user = User.query.get(user_id)
    if not user:
        return []
    
    return [role.name for role in user.roles]

def get_user_permissions(user_id):
    """
    Obtiene los permisos de un usuario basados en sus roles.
    """
    user = User.query.get(user_id)
    if not user:
        return []
    
    permissions = set()
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission.name)
    
    return list(permissions)

def has_role(user_id, role_name):
    """
    Verifica si un usuario tiene un rol específico.
    """
    roles = get_user_roles(user_id)
    return role_name in roles

def has_permission(user_id, permission_name):
    """
    Verifica si un usuario tiene un permiso específico.
    """
    permissions = get_user_permissions(user_id)
    return permission_name in permissions
```

### Ejemplo de Uso

```python
# Ruta protegida por rol
@app.route('/admin/settings', methods=['GET'])
@role_required('admin')
def admin_settings():
    # Solo accesible para administradores
    return jsonify({"settings": get_system_settings()})

# Ruta protegida por permiso
@app.route('/campaigns', methods=['POST'])
@permission_required('create_campaigns')
def create_campaign():
    # Accesible para usuarios con permiso 'create_campaigns'
    data = request.get_json()
    campaign = create_new_campaign(data)
    return jsonify({"campaign": campaign}), 201
```

## Auditoría de Acceso

AdFlux implementa un sistema de auditoría para registrar eventos relacionados con la autenticación y autorización:

```python
class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)
    resource_type = db.Column(db.String(50), nullable=True)
    resource_id = db.Column(db.String(50), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    endpoint = db.Column(db.String(255), nullable=True)
    method = db.Column(db.String(10), nullable=True)
    status_code = db.Column(db.Integer, nullable=True)
    details = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

Eventos registrados:

- Inicios de sesión (exitosos y fallidos)
- Cierres de sesión
- Cambios de contraseña
- Activación/desactivación de 2FA
- Cambios en roles y permisos
- Accesos a recursos protegidos
- Intentos de acceso no autorizados

## Mejores Prácticas

### Para Desarrolladores

1. **Utilizar los Decoradores de Autorización**: Proteger todas las rutas con los decoradores apropiados.
2. **Verificar Permisos en el Frontend**: Ocultar o deshabilitar elementos de UI basados en permisos.
3. **No Confiar en Verificaciones del Cliente**: Siempre verificar permisos en el servidor.
4. **Principio de Privilegio Mínimo**: Asignar solo los permisos necesarios para cada rol.
5. **Auditar Accesos**: Registrar eventos de autenticación y autorización para análisis posterior.

### Para Administradores

1. **Revisión Regular de Roles**: Revisar y actualizar roles y permisos periódicamente.
2. **Rotación de Credenciales**: Forzar cambios de contraseña periódicos.
3. **Monitorización de Actividad**: Revisar logs de auditoría para detectar actividad sospechosa.
4. **Aplicar 2FA**: Requerir 2FA para roles con acceso a información sensible.
5. **Principio de Necesidad de Conocimiento**: Asignar roles basados en las necesidades reales del usuario.

## Recursos Adicionales

- [Documentación de Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- [Documentación de PyOTP (para 2FA)](https://pyauth.github.io/pyotp/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
