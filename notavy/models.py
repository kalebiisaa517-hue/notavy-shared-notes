from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
	class ThemeType(models.TextChoices):
		EMBER = 'EMB', 'ember'
		MIDNGT = 'MID', 'midnight'
		FOREST = 'FOR', 'forest'
		ROSE = 'ROS', 'rose'
		PAPER = 'PAP', 'paper'
	
	class ModeType(models.TextChoices):
		DARK = 'DRK', 'dark'
		LIGHT = 'LGT', 'light'
	
	avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
	email = models.EmailField(unique=True)
	theme = models.CharField(
		max_length=3,
		default=ThemeType.EMBER
	)
	mode = models.CharField(
		max_length=3,
		default=ModeType.DARK
	)
	friends = models.ManyToManyField(
		'self',
		through='Follow',
		symmetrical=False,
	)
	is_public = models.BooleanField(default=False)
	
	REQUIRED_FIELDS = ['email']
	
	class Meta:
		verbose_name = 'Usuário'
		verbose_name_plural = 'Usuários'
	
	def __str__(self):
		return self.username

class Follow(models.Model):
	user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rel_from')
	user_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rel_to')
	
	created_at = models.DateTimeField(auto_now_add=True)
	accepted = models.BooleanField(default=False)
	
	class Meta:
		unique_together = ('user_from', 'user_to')
	
	def __str__(self):
		return f'{self.user_from} seguiu {self.user_to}'

class Note(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name='notes')
	title = models.CharField(max_length=50, blank=False)
	content = models.TextField()
	shared_with = models.ManyToManyField(
		User,
		related_name="shared_me",
		blank=True
	)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return f'{self.title} ({self.user})'
