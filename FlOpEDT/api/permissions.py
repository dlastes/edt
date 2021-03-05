
from rest_framework.permissions import SAFE_METHODS, BasePermission

# -----------------
# -- CUSTOM PERM --
# -----------------

# SAFE_METHODS contains GET, HEAD and OPTIONS methods. These methods are used to retrieve data and not alter them on the database.

# This permission allow only tutor to use all of the methods
class IsTutor(BasePermission):
    message = 'All methods reserved for tutors'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user.is_authenticated and request.user.is_tutor)	


# This permission allow only tutors to use the POST, PUT, PATCH and DELETE methods. GET method can be use by everyone
class IsTutorOrReadOnly(BasePermission):
    message = 'POST, PUT, PATCH and DELETE methods reserved for tutors'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user.is_authenticated and request.user.is_tutor)


# This permission allow only students to use the POST, PUT, PATCH and DELETE methods. GET method can be use by everyone
class IsStudentOrReadOnly(BasePermission):
	message = 'POST, PUT, PATCH and DELETE methods reserved for students'

	def has_permission(self, request, view):
		if request.method in SAFE_METHODS:
			return True
		return bool(request.user.is_authenticated and request.user.is_student)


# This permission allow only admins to use the POST, PUT, PATCH and DELETE methods. GET method can be use by everyone
class IsAdminOrReadOnly(BasePermission):
	message = 'POST, PUT, PATCH and DELETE methods reserved for admin'

	def has_permission(self, request, view):
		if request.method in SAFE_METHODS:
			return True
		return bool(request.user.is_authenticated and request.user.is_superuser)
