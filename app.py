import pickle
import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------------------- Fetch poster safely ----------------------
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=ff957cff0627dbbc70843d3b15c624ff&language=en-US"
    
    # Retry strategy
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    
    try:
        data = session.get(url, timeout=5).json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            full_path = "https://via.placeholder.com/500x750?text=No+Image"
        return full_path
    except requests.exceptions.RequestException as e:
        print("Error fetching poster:", e)
        return "https://via.placeholder.com/500x750?text=No+Image"

# ---------------------- Recommendation logic ----------------------
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_movies_name = []
    recommended_movies_poster = []

    for i in distances[1:6]:  # top 5 recommendations
        movie_id = movies.iloc[i[0]].movie_id
        poster_url = fetch_poster(movie_id)  # call fetch_poster only once
        print("Movie ID:", movie_id)
        print("Poster URL:", poster_url)

        recommended_movies_name.append(movies.iloc[i[0]].title)
        recommended_movies_poster.append(poster_url)

    return recommended_movies_name, recommended_movies_poster

# ---------------------- Streamlit UI ----------------------
st.title("🎬 Movie Recommendation System using Machine Learning")

# Load movie list and similarity matrix
movies = pickle.load(open('artificats/movie_list.pkl', "rb"))
similarity = pickle.load(open('artificats/similarity.pkl', "rb"))

movie_list = movies['title'].values
selected_movie = st.selectbox('Type or select a movie for recommendation', movie_list)

if st.button('Show Recommendation'):
    recommended_movies_name, recommended_movies_poster = recommend(selected_movie)
    
    print("Recommended Movies:", recommended_movies_name)
    print("Recommended Poster URLs:", recommended_movies_poster)
    
    # Display recommendations in 5 columns
    cols = st.columns(5)
    for i in range(len(recommended_movies_name)):
        with cols[i]:
            st.text(recommended_movies_name[i])
            st.image(recommended_movies_poster[i])
