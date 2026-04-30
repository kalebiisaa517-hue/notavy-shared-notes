from django.contrib import admin
from .models import User, Note

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display  = ('username', 'email')

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
	list_display = (
		'user',
		'title',
		'content',
		'created',
		'updated'
	)
