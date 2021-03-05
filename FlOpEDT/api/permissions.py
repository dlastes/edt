
from rest_framework.permissions import SAFE_METHODS, BasePermission

# -----------------
# -- CUSTOM PERM --
# -----------------

class IsTutorOrReadOnly(BasePermission):
    message = 'POST, PUT, PATCH and DELETE methods reserved for tutors'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user.is_authenticated and request.user.is_tutor)

class IsStudentOrReadOnly(BasePermission):
	message = 'POST, PUT, PATCH and DELETE methods reserved for students'

	def has_permission(self, request, view):
		if request.method in SAFE_METHODS:
			return True
		return bool(request.user.is_authenticated and request.user.is_student)

class IsAdminUserOrReadOnly(BasePermission):
	message = 'POST, PUT, PATCH and DELETE methods reserved for admin'

	def has_permission(self, request, view):
		if request.method in SAFE_METHODS:
			return True
		return bool(request.user.is_authenticated and request.user.is_staff)
