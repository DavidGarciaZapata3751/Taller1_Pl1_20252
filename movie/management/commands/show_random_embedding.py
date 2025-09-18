import os
import numpy as np
import random
from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv

class Command(BaseCommand):
    help = "Muestra en la terminal los embeddings de una película elegida al azar"

    def handle(self, *args, **kwargs):
        # Cargar API key
        load_dotenv('openAI.env')
        client = OpenAI(api_key=os.environ.get('openai_apikey'))

        # Escoger una película aleatoria
        movies = list(Movie.objects.all())
        if not movies:
            self.stderr.write("❌ No hay películas en la base de datos")
            return

        movie = random.choice(movies)
        self.stdout.write(self.style.WARNING(f"🎬 Película seleccionada: {movie.title}"))

        # Obtener embedding
        response = client.embeddings.create(
            input=[movie.description],
            model="text-embedding-3-small"
        )
        emb = np.array(response.data[0].embedding, dtype=np.float32)

        # Mostrar vector de embeddings (primeros 50 valores para no saturar)
        self.stdout.write(self.style.SUCCESS("📊 Embeddings (primeros 50 valores):"))
        self.stdout.write(str(emb[:50]))

        # Si quieres mostrar todos, quita el [:50]
        # self.stdout.write(str(emb))
