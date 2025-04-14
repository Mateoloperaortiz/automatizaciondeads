"""
Pruebas unitarias para modelos de AdFlux.

Este módulo contiene pruebas unitarias para los modelos de base de datos de AdFlux.
"""

import pytest
from datetime import datetime, timedelta

from adflux.models import User, Role, Permission, Campaign, MetaCampaign
from adflux.auth.rbac import get_user_permissions, get_user_roles


@pytest.mark.unit
@pytest.mark.models
class TestUserModel:
    """Pruebas para el modelo User."""
    
    def test_create_user(self, db):
        """Prueba la creación de un usuario."""
        # Crear usuario
        user = User(
            username='testuser',
            email='test@example.com',
            name='Test User',
            password_hash='hash',
            active=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Verificar que el usuario se creó correctamente
        saved_user = User.query.filter_by(username='testuser').first()
        assert saved_user is not None
        assert saved_user.email == 'test@example.com'
        assert saved_user.name == 'Test User'
        assert saved_user.active is True
    
    def test_user_roles(self, db):
        """Prueba la asignación de roles a un usuario."""
        # Crear usuario
        user = User(
            username='roleuser',
            email='role@example.com',
            name='Role User',
            password_hash='hash',
            active=True
        )
        
        # Obtener roles
        admin_role = Role.query.filter_by(name='admin').first()
        editor_role = Role.query.filter_by(name='editor').first()
        
        # Asignar roles
        user.roles.append(admin_role)
        user.roles.append(editor_role)
        
        db.session.add(user)
        db.session.commit()
        
        # Verificar roles
        saved_user = User.query.filter_by(username='roleuser').first()
        assert len(saved_user.roles) == 2
        assert admin_role in saved_user.roles
        assert editor_role in saved_user.roles
        
        # Verificar con función auxiliar
        roles = get_user_roles(saved_user.id)
        assert 'admin' in roles
        assert 'editor' in roles
    
    def test_user_permissions(self, db):
        """Prueba los permisos de un usuario a través de sus roles."""
        # Crear usuario
        user = User(
            username='permuser',
            email='perm@example.com',
            name='Permission User',
            password_hash='hash',
            active=True
        )
        
        # Obtener rol
        editor_role = Role.query.filter_by(name='editor').first()
        
        # Asignar rol
        user.roles.append(editor_role)
        
        db.session.add(user)
        db.session.commit()
        
        # Verificar permisos
        permissions = get_user_permissions(user.id)
        assert 'view_campaigns' in permissions
        assert 'create_campaigns' in permissions
        assert 'edit_campaigns' in permissions
        assert 'view_candidates' in permissions
        
        # Verificar que no tiene permisos de administrador
        assert 'delete_users' not in permissions
        assert 'edit_settings' not in permissions


@pytest.mark.unit
@pytest.mark.models
class TestCampaignModel:
    """Pruebas para el modelo Campaign."""
    
    def test_create_campaign(self, db, admin_user):
        """Prueba la creación de una campaña."""
        # Crear campaña
        campaign = Campaign(
            name='Test Campaign',
            objective='AWARENESS',
            status='DRAFT',
            platform='META',
            daily_budget=100.0,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            created_by=admin_user.id
        )
        
        db.session.add(campaign)
        db.session.commit()
        
        # Verificar que la campaña se creó correctamente
        saved_campaign = Campaign.query.filter_by(name='Test Campaign').first()
        assert saved_campaign is not None
        assert saved_campaign.objective == 'AWARENESS'
        assert saved_campaign.status == 'DRAFT'
        assert saved_campaign.platform == 'META'
        assert saved_campaign.daily_budget == 100.0
        assert saved_campaign.created_by == admin_user.id
    
    def test_campaign_meta_campaign_relationship(self, db, admin_user):
        """Prueba la relación entre Campaign y MetaCampaign."""
        # Crear campaña
        campaign = Campaign(
            name='Meta Campaign Test',
            objective='AWARENESS',
            status='ACTIVE',
            platform='META',
            daily_budget=100.0,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            created_by=admin_user.id
        )
        
        db.session.add(campaign)
        db.session.commit()
        
        # Crear campaña de Meta asociada
        meta_campaign = MetaCampaign(
            campaign_id=campaign.id,
            external_id='123456789',
            status='ACTIVE'
        )
        
        db.session.add(meta_campaign)
        db.session.commit()
        
        # Verificar relación
        saved_campaign = Campaign.query.filter_by(name='Meta Campaign Test').first()
        assert saved_campaign is not None
        assert saved_campaign.meta_campaign is not None
        assert saved_campaign.meta_campaign.external_id == '123456789'
        assert saved_campaign.meta_campaign.status == 'ACTIVE'
        
        # Verificar relación inversa
        saved_meta_campaign = MetaCampaign.query.filter_by(external_id='123456789').first()
        assert saved_meta_campaign is not None
        assert saved_meta_campaign.campaign is not None
        assert saved_meta_campaign.campaign.name == 'Meta Campaign Test'
    
    def test_campaign_status_transitions(self, db, admin_user):
        """Prueba las transiciones de estado de una campaña."""
        # Crear campaña
        campaign = Campaign(
            name='Status Test Campaign',
            objective='AWARENESS',
            status='DRAFT',
            platform='META',
            daily_budget=100.0,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            created_by=admin_user.id
        )
        
        db.session.add(campaign)
        db.session.commit()
        
        # Verificar estado inicial
        assert campaign.status == 'DRAFT'
        
        # Cambiar a PENDING
        campaign.status = 'PENDING'
        db.session.commit()
        
        # Verificar cambio
        saved_campaign = Campaign.query.get(campaign.id)
        assert saved_campaign.status == 'PENDING'
        
        # Cambiar a ACTIVE
        campaign.status = 'ACTIVE'
        db.session.commit()
        
        # Verificar cambio
        saved_campaign = Campaign.query.get(campaign.id)
        assert saved_campaign.status == 'ACTIVE'
        
        # Cambiar a PAUSED
        campaign.status = 'PAUSED'
        db.session.commit()
        
        # Verificar cambio
        saved_campaign = Campaign.query.get(campaign.id)
        assert saved_campaign.status == 'PAUSED'
        
        # Cambiar a COMPLETED
        campaign.status = 'COMPLETED'
        db.session.commit()
        
        # Verificar cambio
        saved_campaign = Campaign.query.get(campaign.id)
        assert saved_campaign.status == 'COMPLETED'


@pytest.mark.unit
@pytest.mark.models
class TestRolePermissionModel:
    """Pruebas para los modelos Role y Permission."""
    
    def test_create_role(self, db):
        """Prueba la creación de un rol."""
        # Crear rol
        role = Role(
            name='test_role',
            description='Test Role'
        )
        
        db.session.add(role)
        db.session.commit()
        
        # Verificar que el rol se creó correctamente
        saved_role = Role.query.filter_by(name='test_role').first()
        assert saved_role is not None
        assert saved_role.description == 'Test Role'
    
    def test_create_permission(self, db):
        """Prueba la creación de un permiso."""
        # Crear permiso
        permission = Permission(
            name='test_permission',
            description='Test Permission'
        )
        
        db.session.add(permission)
        db.session.commit()
        
        # Verificar que el permiso se creó correctamente
        saved_permission = Permission.query.filter_by(name='test_permission').first()
        assert saved_permission is not None
        assert saved_permission.description == 'Test Permission'
    
    def test_role_permission_relationship(self, db):
        """Prueba la relación entre Role y Permission."""
        # Crear rol
        role = Role(
            name='relation_role',
            description='Relation Test Role'
        )
        
        # Crear permisos
        permission1 = Permission(
            name='test_permission1',
            description='Test Permission 1'
        )
        
        permission2 = Permission(
            name='test_permission2',
            description='Test Permission 2'
        )
        
        # Asignar permisos al rol
        role.permissions.append(permission1)
        role.permissions.append(permission2)
        
        db.session.add_all([role, permission1, permission2])
        db.session.commit()
        
        # Verificar relación
        saved_role = Role.query.filter_by(name='relation_role').first()
        assert saved_role is not None
        assert len(saved_role.permissions) == 2
        assert permission1 in saved_role.permissions
        assert permission2 in saved_role.permissions
        
        # Verificar relación inversa
        saved_permission1 = Permission.query.filter_by(name='test_permission1').first()
        assert saved_permission1 is not None
        assert saved_role in saved_permission1.roles
        
        saved_permission2 = Permission.query.filter_by(name='test_permission2').first()
        assert saved_permission2 is not None
        assert saved_role in saved_permission2.roles
