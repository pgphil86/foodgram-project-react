from rest_framework.permissions import BasePermission


class AuthorPermissions(BasePermission):

    def has_object_permission(self, request, view, obj):
        return bool(request.user == obj.author
                    or request.method not in ('PATCH', 'DELETE'))
