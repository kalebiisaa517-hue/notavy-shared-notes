from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.response import Response 
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer, NoteSerializer
from .models import Note, Follow
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	parser_classes = [MultiPartParser, FormParser, JSONParser]
	lookup_field = 'username'
	
	def get_permissions(self):
		if self.action == 'create':
			return [AllowAny()]
		return [IsAuthenticated()]
	
	@action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
	def me(self, request):
		if request.method == 'PATCH':
			serializer = self.get_serializer(request.user, data=request.data, partial=True)
			serializer.is_valid(raise_exception=True)
			serializer.save()
		else:
			serializer = self.get_serializer(request.user)
		
		return Response(serializer.data)
	
	@action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
	def theme_prefer(self, request):
		user = request.user
		
		if request.method == 'PATCH':
			serializer = self.get_serializer(user, data=request.data, partial=True)
			serializer.is_valid(raise_exception=True)
			user = serializer.save()
		
		
		theme_id = user.theme
		mode_id = user.mode
		
		return Response(
			{
				"theme": theme_id,
				"mode": mode_id
			}
		)
	
	@action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
	def followers(self, request):
		return Response(self.get_serializer(request.user).data['followers'])
	
	@action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
	def following(self, request):
		return Response(self.get_serializer(request.user).data['following'])
	
	@action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
	def follow(self, request, username=None):
		user = request.user
		follow_user = self.get_object()
		
		if user == follow_user:
			return Response({"detail": "Você não pode se seguir."}, status=400)
		
		follow, created = Follow.objects.get_or_create(user_from=user, user_to=follow_user, defaults={"accepted": follow_user.is_public})
		
		if not created:
			return Response({"detail": "Pedido já foi enviado"}, status=400)
		return Response({"detail":"Pedido enviado."}, status=201)
	
	@action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
	def accept_follow(self, request, username=None):
		user = request.user
		user_from = self.get_object()
		follow = get_object_or_404(Follow, user_from=user_from, user_to=user, accepted=False)
		follow.accepted = True
		follow.save()
		
		return Response({"detail": "Pedido aceito."})
		#Follow.objects.update(follow, {"user_from": user_from, "user_to": user, "accepted": True})
	
	@action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
	def reject_delete_follow(self, request, username=None):
		user = request.user
		user_from = self.get_object()
		follow = get_object_or_404(Follow, user_from=user_from, user_to=user)
		follow.delete()
		
		return Response({"detail": "Seguidor rejeitado/excluido."})
	
	@action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
	def delete_requested_following(self, request, username=None):
		user = request.user
		user_to = self.get_object()
		follow = get_object_or_404(Follow, user_from=user, user_to=user_to)
		follow.delete()
		
		return Response({"detail": "Parou/excluiu de seguir"})
	
	@action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
	def notes(self, request):
		serializer = NoteSerializer(request.user.notes.all(), many=True)
		return Response(serializer.data)
	
	@action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
	def shared_notes(self, request):
		serializer = NoteSerializer(request.user.shared_me.all(), many=True)
		
		return Response(serializer.data)
	
	@action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
	def public_or_private(self, request):
		user = request.user
		user.is_public = not user.is_public
		user.save()
		
		return Response({"Is public: ": user.is_public})

class NoteViewSet(viewsets.ModelViewSet):
	queryset = Note.objects.all()
	serializer_class = NoteSerializer
	permission_classes = [IsAuthenticated]
	
	http_method_names = ['get', 'post', 'delete', 'patch']
	
	def get_queryset(self):
		return Note.objects.filter(
			Q(user=self.request.user) | Q(shared_with=self.request.user)
		).distinct()
	
	def perform_create(self, serializer):
		serializer.save(user=self.request.user)
	
	@action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
	def share_note(self, request, pk=None):
		note = self.get_object()
		share_user = get_object_or_404(User, username=request.data.get('share_user'))
		
		if note.user != request.user:
			return Response({"detail": "Só é possível compartilhar notas suas."}, status=400)
		
		note.shared_with.add(share_user)
		
		return Response({"detail": "Nota compartilhada!"}, status=201)
