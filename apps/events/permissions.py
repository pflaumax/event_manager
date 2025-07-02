from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import View
from typing import Any


class IsCreatorOrReadOnly(BasePermission):
    """
    Custom permission to only allow creators of an object to edit/delete it.
    Other users can only read (GET, HEAD, OPTIONS).
    """

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """
        Check if user has permission to perform action on object.
        Args:
            request: HTTP request object
            view: View being accessed
            obj: Object being accessed
        Returns:
            bool: True if user has permission, False otherwise
        """
        if request.method in SAFE_METHODS:
            return True
        return obj.created_by == request.user
