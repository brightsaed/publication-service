from rest_framework import permissions


class IsEditor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ('editor', 'moderator', 'admin')


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ('moderator', 'admin')


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin'