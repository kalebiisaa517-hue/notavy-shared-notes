from django.apps import AppConfig


class NotavyConfig(AppConfig):
    name = 'notavy'
    
    def ready(self):
    	import notavy.signals
