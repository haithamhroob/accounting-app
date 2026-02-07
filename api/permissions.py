"""
Custom Permission Classes for Role-Based Access Control (RBAC)
صلاحيات مخصصة للتحكم بالوصول حسب الدور
"""
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Full access for Admin users only
    وصول كامل للمسؤولين فقط
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_superuser or request.user.groups.filter(name='Admin').exists())
        )


class IsAccountant(permissions.BasePermission):
    """
    Full CRUD access for Accountants on financial data
    وصول كامل للمحاسبين على البيانات المالية
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
            
        return request.user.groups.filter(name__in=['Admin', 'Accountant']).exists()


class IsClerk(permissions.BasePermission):
    """
    Create/Read access for Clerks (no delete)
    إنشاء/قراءة للكتبة (بدون حذف)
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Clerks can only read and create
        if request.method in ['DELETE']:
            return request.user.groups.filter(name__in=['Admin', 'Accountant']).exists()
        
        return request.user.groups.filter(name__in=['Admin', 'Accountant', 'Clerk']).exists()


class IsReadOnly(permissions.BasePermission):
    """
    Read-only access for ReadOnly users
    وصول للقراءة فقط
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For write operations, check higher roles
        return request.user.groups.filter(name__in=['Admin', 'Accountant', 'Clerk']).exists()


class RoleBasedPermission(permissions.BasePermission):
    """
    Main permission class that combines all role checks
    الصلاحية الرئيسية التي تجمع كل فحوصات الأدوار
    """
    
    # Map actions to required roles
    ROLE_HIERARCHY = {
        'Admin': 4,
        'Accountant': 3,
        'Clerk': 2,
        'ReadOnly': 1,
    }
    
    ACTION_PERMISSIONS = {
        'list': 1,      # ReadOnly and above
        'retrieve': 1,  # ReadOnly and above
        'create': 2,    # Clerk and above
        'update': 3,    # Accountant and above
        'partial_update': 3,  # Accountant and above
        'destroy': 4,   # Admin only
    }
    
    def get_user_role_level(self, user):
        """Get the highest role level for a user"""
        if user.is_superuser:
            return 4
        
        for role, level in self.ROLE_HIERARCHY.items():
            if user.groups.filter(name=role).exists():
                return level
        
        return 1  # Default to ReadOnly
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        action = getattr(view, 'action', None)
        if action is None:
            # For non-viewset views, use method
            if request.method in permissions.SAFE_METHODS:
                action = 'list'
            elif request.method == 'POST':
                action = 'create'
            elif request.method in ['PUT', 'PATCH']:
                action = 'update'
            elif request.method == 'DELETE':
                action = 'destroy'
        
        required_level = self.ACTION_PERMISSIONS.get(action, 1)
        user_level = self.get_user_role_level(request.user)
        
        return user_level >= required_level
    
    def has_object_permission(self, request, view, obj):
        # Object-level permissions use the same logic
        return self.has_permission(request, view)
