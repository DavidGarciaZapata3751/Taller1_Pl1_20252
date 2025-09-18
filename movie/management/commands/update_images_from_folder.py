from django.core.management.base import BaseCommand
from movie.models import Movie
import os

class Command(BaseCommand):
    help = 'Actualiza las imágenes de las películas desde la carpeta media/movie/images/'

    def handle(self, *args, **kwargs):
        images_folder = 'media/movie/images/'
        updated = 0
        not_found = 0

        for movie in Movie.objects.all():
            # Buscar imagen con el formato m_nombre (nombre en minúsculas, espacios a guion bajo, extensión .png)
            image_name = f"m_{movie.title.lower()}.png"
            image_path = os.path.join(images_folder, image_name)
            if os.path.exists(image_path):
                movie.image = f"movie/images/{image_name}"
                movie.save()
                updated += 1
                self.stdout.write(self.style.SUCCESS(f"Imagen asignada: {movie.title} -> {image_name}"))
            else:
                not_found += 1
                self.stdout.write(self.style.WARNING(f"No se encontró imagen para: {movie.title}"))

        self.stdout.write(self.style.SUCCESS(f"Imágenes actualizadas: {updated}"))
        self.stdout.write(self.style.WARNING(f"Películas sin imagen encontrada: {not_found}"))