from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """
    Custom permission to only allow super admins to access an object.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated and has the 'SuperAdmin' role.
        return request.user and request.user.is_authenticated and request.user.rol.nombre_rol == 'SuperAdmin'

class IsOwnerOfEmpresa(permissions.BasePermission):
    """
    Custom permission to only allow owners of an empresa to manage their objects.
    """

    def has_permission(self, request, view):
        # Allow POST only if the user is creating an object for their own empresa.
        if request.method == 'POST':
            empresa_id = request.data.get('empresa')
            if not empresa_id:
                return False
            return request.user.empresa_asociada_id == int(empresa_id)
        # For other methods, permission is granted at the object level.
        return True

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the empresa.
        return obj.empresa == request.user.empresa_asociada
