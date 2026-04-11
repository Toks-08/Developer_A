from rest_framework.permissions import BasePermission

class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == request.user.Role.INSTRUCTOR
        )

class IsLearner(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == request.user.Role.LEARNER
        )

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == request.user.Role.ADMIN
        )