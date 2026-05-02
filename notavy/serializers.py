from rest_framework import serializers
from .models import User, Note

class UserSerializer(serializers.ModelSerializer):
	following = serializers.SerializerMethodField()
	followers = serializers.SerializerMethodField()
	follow_requests = serializers.SerializerMethodField()
	follow_requested = serializers.SerializerMethodField()
	avatar = serializers.ImageField(required=False, allow_none=True)
	
	def get_following(self, obj):
		return obj.rel_from.filter(accepted=True).values_list('user_to__username', flat=True) or []
	
	def get_followers(self, obj):
		return obj.rel_to.filter(accepted=True).values_list('user_from__username', flat=True) or []
	
	def get_follow_requests(self, obj):
		return obj.rel_to.filter(accepted=False).values_list('user_from__username', flat=True) or []
	
	def get_follow_requested(self, obj):
		return obj.rel_from.filter(accepted=False).values_list('user_to__username', flat=True) or []
	
	class Meta:
		model = User
		fields = [
			'id', 
			'username',
			'password',
			'theme',
			'mode',
			'email',
			'is_public',
			'following',
			'followers',
			'follow_requests',
			'follow_requested'
		]
		extra_kwargs = {
			'password': {
				'write_only': True
			}
		}
	
	def create(self, validated_data):
		return User.objects.create_user(**validated_data)
	
	# protected fields
	def to_representation(self, instance):
		data = super().to_representation(instance)
		
		request = self.context.get('request')
		user = request.user if request else None
		
		if instance != user:
			private_fields = ['email', 'theme', 'mode']
			for field in private_fields:
				data.pop(field, None)
		
		return data

class NoteSerializer(serializers.ModelSerializer):
	user = serializers.CharField(source='user.username', read_only=True)
	
	class Meta:
		model = Note
		fields = [
			'id',
			'user',
			'title',
			'content',
			'created',
			'shared_with',
			'updated'
		]
		read_only_fields = ['user', 'created', 'updated']
