from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrContadorOrAyudanteOrAuditor(BasePermission):
    """
    Controla lo que cada rol puede hacer con las cuentas.
    """

    def has_permission(self, request, view):
        # Solo usuarios autenticados pueden acceder
        if not request.user.is_authenticated:
            return False

        role = request.user.role  

        # ---- Lectura (GET, HEAD, OPTIONS) ----
        if request.method in SAFE_METHODS:
            # Todos los roles pueden leer (admin, contador, ayudante, auditor)
            return True

        # ---- Creación (POST) ----
        if request.method == "POST":
            # Admin, contador y ayudante pueden crear cuentas
            return role in ["admin", "contador", "ayudante"]

        # ---- Actualización (PUT/PATCH) ----
        if request.method in ["PUT", "PATCH"]:
            # Admin y contador pueden modificar cuentas
            return role in ["admin", "contador"]

        # ---- Eliminación (DELETE) ----
        if request.method == "DELETE":
            # Solo admin puede borrar cuentas
            return role == "admin"

        return False
