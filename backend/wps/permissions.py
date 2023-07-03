from django.contrib.auth.models import Group
from rest_framework import permissions


class PermitValidationPermission(permissions.BasePermission):
    """
    Custom permission to only allow users with permissions
    to validate the permit
    """

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if not request.user.app_role_id:
            return False

        app_role = Group.objects.get(pk=request.user.app_role_id)
        return app_role.name == 'Admin'


class PermitObjectPermission(permissions.BasePermission):
    """
    Custom permission to only allow users with permissions
    to view/update/delete the permits.
    """

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            # creator of the permit is allowed to view it
            if request.user == obj.submitted_by:
                return True

            # other (non-admin) users are not allowed to view it
            if not request.user.app_role_id:
                return False

            # admin is allowed to view it
            app_role = Group.objects.get(pk=request.user.app_role_id)
            return app_role.name == 'Admin'

        # non-admin users are not allowed to edit/delete object (even if they created the permit)
        if not request.user.app_role_id:
            return False

        # admin is allowed to view it
        app_role = Group.objects.get(pk=request.user.app_role_id)
        return app_role.name == 'Admin'
