from rest_framework import permissions

class IsAdminOrContadorOrAyudanteOrAuditor(permissions.BasePermission):
    """
    - admin: CRUD completo
    - contador: CRUD completo
    - ayudante: puede crear y leer, pero no borrar
    - auditor: solo lectura
    """

    def has_permission(self, request, view):
        role = getattr(request.user, "role", None)

        if role == "admin" or role == "contador":
            return True

        if role == "ayudante":
            return request.method in permissions.SAFE_METHODS + ("POST", "PUT", "PATCH")

        if role == "auditor":
            return request.method in permissions.SAFE_METHODS

        return False
