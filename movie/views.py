import os
from django.shortcuts import render
from django.http import HttpResponse
from .models import Movie
import matplotlib.pyplot as plt
import matplotlib
import io 
import urllib, base64
import numpy as np
from django.shortcuts import render
from django.http import HttpResponse
from .models import Movie
matplotlib.use('Agg')              # Backend sin ventana (recomendado en servidores)
from collections import Counter
from openai import OpenAI
from dotenv import load_dotenv
# Create your views here.
load_dotenv('openAI.env')
MODEL = "text-embedding-3-small"
CLIENT = OpenAI(api_key=os.environ.get("openai_apikey"))


def home(request):
    searchTerm = request.GET.get('searchMovie')

    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()

    return render(request, 'home.html', {
        'searchTerm': searchTerm,
        'movies': movies
    })

def recommendation(request):
    q = request.GET.get("searchMovie")
    if not q:
        return render(request, "recommendation.html", {
            "searchTerm": q,
            "movies": Movie.objects.all()[:20]
        })

    # 1) Embedding de la consulta
    q_vec = embed_text(q)

    # 2) Comparar contra cada película con emb guardado
    scored = []
    for m in Movie.objects.exclude(emb=None):
        v = bytes_to_vec(m.emb)
        if v is None or v.size == 0:
            continue
        s = cosine(q_vec, v)
        m.similarity = s   # atributo temporal para la plantilla
        scored.append(m)

    # 3) Ordenar por similitud descendente
    scored.sort(key=lambda x: x.similarity, reverse=True)
    movies = scored[:20]

    return render(request, "recommendation.html", {
        "searchTerm": q,
        "movies": movies
    })


def bytes_to_vec(b: bytes) -> np.ndarray:
    if b is None:
        return None
    return np.frombuffer(b, dtype=np.float32)

def embed_text(text: str) -> np.ndarray:
    if not os.environ.get("openai_apikey"):
        raise RuntimeError("Falta la variable de entorno 'openai_apikey'.")
    resp = CLIENT.embeddings.create(input=[text], model=MODEL)
    return np.array(resp.data[0].embedding, dtype=np.float32)

def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))




def about(request):
    return render(request, 'about.html')

# movie/views.py



# movie/views.py
from django.shortcuts import render
from .models import Movie

import io
import base64
import matplotlib
matplotlib.use('Agg')                     # backend sin UI
import matplotlib.pyplot as plt
from collections import Counter


def statistics_view(request):
    # ======================
    # 1) Traer películas
    # ======================
    all_movies = Movie.objects.all()

    # ======================
    # 2) Gráfica: Movies per year
    # ======================
    years = [m.year for m in all_movies if getattr(m, 'year', None) is not None]
    counts_by_year = Counter(years)

    years_sorted = sorted(counts_by_year.keys())
    year_values = [counts_by_year[y] for y in years_sorted]
    year_positions = range(len(years_sorted))

    plt.figure(figsize=(8, 4))
    plt.bar(year_positions, year_values, width=0.5, align='center')
    plt.title('Movies per year')
    plt.xlabel('Year')
    plt.ylabel('Number of movies')
    plt.xticks(year_positions, years_sorted, rotation=90)
    plt.subplots_adjust(bottom=0.3)

    buf_year = io.BytesIO()
    plt.savefig(buf_year, format='png', bbox_inches='tight')
    buf_year.seek(0)
    graphic_year = base64.b64encode(buf_year.getvalue()).decode('utf-8')
    buf_year.close()
    plt.close()

    # ==========================================
    # 3) Gráfica: Movies per genre (FIRST genre)
    # ==========================================
    def first_genre_of(movie):
        """
        Devuelve el PRIMER género de la película:
        - Si hay ManyToMany 'genres' -> toma el primero por .first().name
        - Si hay CharField 'genre' (posible lista separada por comas/ / | ;) -> toma el primer trozo
        - Si no hay info -> None
        """
        # Caso ManyToMany (genres)
        if hasattr(movie, 'genres'):
            first = movie.genres.all().first()
            return getattr(first, 'name', None) if first else None

        # Caso CharField (genre)
        g = getattr(movie, 'genre', None)
        if g is None:
            return None
        if isinstance(g, str):
            text = g.strip()
            if not text:
                return None
            for sep in [',', '/', '|', ';']:
                if sep in text:
                    return text.split(sep)[0].strip()
            return text  # solo un género en el string
        return str(g)

    first_genres = [first_genre_of(m) for m in all_movies]
    first_genres = [g for g in first_genres if g]  # quitar None/''

    counts_by_genre = Counter(first_genres)
    genres_sorted = sorted(counts_by_genre.keys())
    genre_values = [counts_by_genre[g] for g in genres_sorted]
    genre_positions = range(len(genres_sorted))

    plt.figure(figsize=(8, 4))
    plt.bar(genre_positions, genre_values, width=0.5, align='center')
    plt.title('Movies per genre (first genre only)')
    plt.xlabel('Genre')
    plt.ylabel('Number of movies')
    plt.xticks(genre_positions, genres_sorted, rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.35)

    buf_genre = io.BytesIO()
    plt.savefig(buf_genre, format='png', bbox_inches='tight')
    buf_genre.seek(0)
    graphic_genre = base64.b64encode(buf_genre.getvalue()).decode('utf-8')
    buf_genre.close()
    plt.close()

    # ======================
    # 4) Render
    # ======================
    return render(
        request,
        'statistics.html',
        {
            'graphic_year': graphic_year,
            'graphic_genre': graphic_genre,
        }
    )

def signup(request):
    email = request.GET.get('email')
    return render(request, 'signup.html', {'email': email})

 
