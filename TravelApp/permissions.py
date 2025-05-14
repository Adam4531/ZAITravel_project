from rest_framework import permissions


class IsReservedOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if obj.user == request.user:
            return True
        return False
