from rest_framework.routers import SimpleRouter
from .views import UserViewSet, NoteViewSet

router = SimpleRouter()
router.register('users', UserViewSet)
router.register('notes', NoteViewSet)
