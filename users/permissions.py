from rest_framework import permissions


class IsModer(permissions.BasePermission):
    """
    Проверка, является пользователь модератором или нет.
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name="Moders").exists()


class NotModer(permissions.BasePermission):
    """
    Проверка, что пользователь НЕ модератор.
    """
    def has_permission(self, request, view):
        return not request.user.groups.filter(name="Moders").exists()


class IsOwner(permissions.BasePermission):
    """
        Проверка, является пользователь владельцем или нет.
    """

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return False
