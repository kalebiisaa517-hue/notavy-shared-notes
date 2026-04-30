from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from .models import Note

User = get_user_model()

@receiver(post_save, sender=User)
def create_tutorial_note(sender, instance, created, **kwargs):
	if created:
		Note.objects.create(
			user=instance,
			title="Bem-vindo!",
			content="""1. Comece configurando o tema! **Configurações** > **Tema** 2. Crie sua primeira nota, definindo o título e conteúdo. Use a barra de ferramentas para customização. 3. Salve a sua nota, e edite quando quiser."""
		)
