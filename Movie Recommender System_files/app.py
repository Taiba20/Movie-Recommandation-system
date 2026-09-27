import pickle
import pandas as pd
import streamlit as st
import requests

# ── TMDB API ──────────────────────────────────────────────────────────────────
TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"  # public demo key
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"
PLACEHOLDER_IMG = "https://via.placeholder.com/500x750?text=No+Image"


def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        data = requests.get(url, timeout=5).json()
        path = data.get("poster_path")
        return (TMDB_IMG_BASE + path) if path else PLACEHOLDER_IMG
    except Exception:
        return PLACEHOLDER_IMG


# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    movies = pickle.load(open("Movie Recommender System_files/movie_list.pkl", "rb"))
    similarity = pickle.load(open("Movie Recommender System_files/similarity.pkl", "rb"))
    if not isinstance(movies, pd.DataFrame):
        movies = pd.DataFrame(movies)
    return movies, similarity


movies, similarity = load_data()


# ── Recommendation logic ───────────────────────────────────────────────────────
def recommend(movie_title):
    idx = movies[movies["title"] == movie_title].index[0]
    pos = movies.index.get_loc(idx)
    scores = sorted(enumerate(similarity[pos]), key=lambda x: x[1], reverse=True)[1:6]
    results = []
    for i, _ in scores:
        row = movies.iloc[i]
        results.append({
            "title": row["title"],
            "poster": fetch_poster(row["movie_id"]),
        })
    return results


# ── UI ────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

st.title("🎬 Movie Recommender System")
st.markdown("Select a movie and get 5 similar recommendations instantly.")

selected = st.selectbox("Choose a movie", movies["title"].values)

if st.button("Recommend", type="primary"):
    with st.spinner("Finding recommendations..."):
        recs = recommend(selected)

    st.markdown("---")
    st.subheader("Top 5 Recommendations")
    cols = st.columns(5)
    for col, movie in zip(cols, recs):
        with col:
            st.image(movie["poster"], use_container_width=True)
            st.markdown(f"**{movie['title']}**")
