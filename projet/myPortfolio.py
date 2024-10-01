import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium
import base64
from myProfile import *
from DataVIz import *

st.sidebar.markdown(
    """
    <style>
    .profile-pic-container {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    .profile-pic {
        border-radius: 50%;
        width: 150px;
        height: 150px;
        object-fit: cover;
    }
    </style>
    """,
    unsafe_allow_html=True
)



image_path = "photo_profil.png"

# Convertir l'image en base64 pour l'inclure dans le HTML
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    return encoded_image

# Afficher la photo de profil dans la barre latérale
with st.sidebar:
    image_base64 = get_base64_image(image_path)
    st.markdown(
        f"""
        <div class="profile-pic-container">
            <img src="data:image/png;base64,{image_base64}" class="profile-pic">
        </div>
        """,
        unsafe_allow_html=True
    )

st.sidebar.title("Contact Information 📞:")
st.sidebar.info("""
Constance Walusiak  
[LinkedIn](https://www.linkedin.com/in/constance-walusiak-data-ia/)  
**Email**: constance.walusiak@efrei.net  
[GitHub](https://github.com/ConstanceWk)
""")

# Sélection de la page
page = st.sidebar.selectbox("Select the page", ["Biographie", "Visualisation"])

# Affichage de la page correspondante
if page == "Biographie":
    page_biographie()
else:
    page_data_visualisation()
