import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from functions import *
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import numpy as np

# In this file, we have all functions to data visualize.

def load_geojson(local_path):
    # we load the geojson file to have the coordinates of regions
    gdf = gpd.read_file(local_path)
    return gdf

def load_data(filepath):
    # This function is for charging the csv file for our data
    df = pd.read_csv(filepath, delimiter=';')
    return df

def print_table(df):
    # this function is for printing all we want to see from the data in our dataset 

    all_columns = df.columns.tolist()
    selected_columns = st.multiselect(
        'Select columns to display', 
        options=all_columns, 
        default=all_columns[:5] 
    )

    selected_filter_column = st.selectbox('Select a column to filter', options=all_columns)

    if selected_filter_column:
        unique_values = df[selected_filter_column].unique().tolist()
        selected_value = st.selectbox(f'Select a value from {selected_filter_column}', options=unique_values)
        filtered_df = df[df[selected_filter_column] == selected_value]

        if selected_columns:
            num_rows = min(5, len(filtered_df))

            if num_rows > 0:
                random_rows = filtered_df[selected_columns].sample(n=num_rows)
                st.write(f"Here are some random rows for '{selected_value}' from the selected columns:")
                st.dataframe(random_rows)
            else:
                st.write(f"No data available for {selected_value} in column {selected_filter_column}.")

def plot_pie_chart(df):
    
    # This function is for visualize the classe for each region
    st.header("Visualisation dynamique par classe")
    
    classe_selected = st.selectbox("Sélectionnez une classe pour la visualisation", df['classe'].unique())
    filtered_data = df[df['classe'] == classe_selected]
    data_grouped = filtered_data.groupby('Code.région')['faits'].sum().reset_index()
    fig = px.pie(data_grouped, names='Code.région', values='faits', 
                 title=f"Répartition des faits pour la classe '{classe_selected}'")

    st.plotly_chart(fig)

def plot_mapbox(df, gdf):
    # This function is for maping the classe you want in France map
    st.header("Carte interactive choroplèthe avec Mapbox")
    classe_selected = st.selectbox("Sélectionnez une classe pour la carte", df['classe'].unique())
 
    filtered_data = df[df['classe'] == classe_selected]
    filtered_data['Code.région'] = filtered_data['Code.région'].astype(str)
    gdf['region_code'] = gdf['code'].astype(str)  

    if not isinstance(gdf, gpd.GeoDataFrame):
        gdf = gpd.GeoDataFrame(gdf, geometry=gpd.GeoSeries(gdf['geometry']))

    merged_data = pd.merge(filtered_data, gdf[['region_code', 'geometry']], 
                           left_on='Code.région', right_on='region_code', how='left')

    merged_data = gpd.GeoDataFrame(merged_data, geometry='geometry') 
    geojson_data = merged_data.__geo_interface__  

    fig = px.choropleth_mapbox(
        merged_data,
        geojson=geojson_data,
        locations='Code.région',
        featureidkey='properties.region_code', 
        color='faits',
        color_continuous_scale="Viridis", 
        mapbox_style="carto-positron",
        zoom=5,
        center={"lat": 46.603354, "lon": 1.888334},  
        opacity=0.6,
        title=f"Répartition des faits pour la classe '{classe_selected}'"
    )
  
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig)

def plot_3d_barchart_map(df, gdf):
    st.header("Carte interactive avec barres 3D distinctes et fond de carte")

    if not isinstance(gdf, gpd.GeoDataFrame):
        gdf = gpd.GeoDataFrame(gdf, geometry=gpd.GeoSeries(gdf['geometry']))
    
    # Conversion des colonnes pour qu'elles aient le même type (string)
    df['Code.région'] = df['Code.région'].astype(str)
    gdf['region_code'] = gdf['code'].astype(str)
    
    # Ajouter les informations de la région via GeoDataFrame
    merged_data = pd.merge(df, gdf[['region_code', 'geometry']], 
                           left_on='Code.région', right_on='region_code', how='left')

    # Conversion des géométries en GeoJSON
    merged_data = gpd.GeoDataFrame(merged_data, geometry='geometry')

    # Création des barres 3D pour chaque région et classe
    fig = go.Figure()

    # Couleurs distinctes pour chaque type de classe
    colors = px.colors.qualitative.Plotly
    classes = df['classe'].unique()
    
    # Décalage pour éviter l'empiètement
    offset = 0.02  # Ajustez cette valeur pour modifier l'écart

    for i, classe in enumerate(classes):
        classe_data = merged_data[merged_data['classe'] == classe]
        
        # Coordonnées des centroids pour les barres
        x = classe_data['geometry'].centroid.x.tolist()
        y = classe_data['geometry'].centroid.y.tolist()
        z = np.zeros(len(classe_data)).tolist()  # Bas des barres
        dz = classe_data['faits'].tolist()  # Hauteur des barres
        
        # Ajouter un décalage pour espacer les barres
        x_offset = [xi + (i * offset) for xi in x]  # Décalage en x
        y_offset = [yi + (i * offset) for yi in y]  # Décalage en y
        
        # Ajout des barres individuelles pour chaque classe
        for j in range(len(x)):
            # Ajouter le nom uniquement pour la première barre de chaque classe
            name = classe if j == 0 else None
            fig.add_trace(go.Scatter3d(
                x=[x_offset[j], x_offset[j], x_offset[j]],  # x est constant pour la barre
                y=[y_offset[j], y_offset[j], y_offset[j]],  # y est constant pour la barre
                z=[0, dz[j], 0],  # Les trois points définissent la barre
                mode='lines',
                line=dict(color=colors[i % len(colors)], width=6),  # Largeur de barre ajustée
                name=name,  # Nom pour la légende (uniquement pour la première barre)
                showlegend=name is not None,  # Afficher la légende uniquement pour la première barre
                hoverinfo='text',  # Informations à afficher au survol
                hovertext=classe  # Texte à afficher au survol
            ))

    # Ajout du fond de carte
    for _, region in gdf.iterrows():
        geometry = region['geometry']
        
        if geometry.geom_type == 'Polygon':
            polygons = [geometry]
        elif geometry.geom_type == 'MultiPolygon':
            polygons = geometry.geoms
        
        for polygon in polygons:
            x, y = polygon.exterior.xy
            fig.add_trace(go.Scatter3d(
                x=list(x),
                y=list(y),
                z=[0]*len(x),
                mode='lines',
                line=dict(color='black', width=2),
                showlegend=False
            ))
    
    # Mise à jour du layout
    fig.update_layout(
        scene=dict(
            xaxis_title='Longitude',
            yaxis_title='Latitude',
            zaxis_title='Nombre de faits',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
        ),
        title="Répartition des faits par région avec barres 3D distinctes et fond de carte",
        margin=dict(r=0, t=0, l=0, b=0),
        showlegend=True
    )

    # Affichage de la carte
    st.plotly_chart(fig)

def courbes_vict_mec(df):

    """Fonction pour visualiser les faits subis par les victimes et réalisés par les mis en cause."""
    
    # Filtrer les données pour les victimes
    df_victimes = df[df['unité.de.compte'] == 'victime']
    
    # Filtrer les données pour les mis en cause
    df_mis_en_cause = df[df['unité.de.compte'] == 'Mis en cause']

    # Création d'un graphique pour les victimes
    fig_victimes = px.bar(df_victimes, 
                          x='Code.région', 
                          y='faits', 
                          color='classe', 
                          title='Faits subis par les victimes',
                          labels={'Code.région': 'Code de région', 'faits': 'Nombre de faits'},
                          text='faits')
    
    # Afficher le graphique des victimes
    st.plotly_chart(fig_victimes)

    # Création d'un graphique pour les mis en cause
    fig_mis_en_cause = px.bar(df_mis_en_cause, 
                              x='Code.région', 
                              y='faits', 
                              color='classe', 
                              title='Faits réalisés par les mis en cause',
                              labels={'Code.région': 'Code de région', 'faits': 'Nombre de faits'},
                              text='faits')
    
    # Afficher le graphique des mis en cause
    st.plotly_chart(fig_mis_en_cause)

def map_taux_crim(df, gdf):
    
    # Calculer le pourcentage de criminalité par région
    df['pourcentage_criminalite'] = (df['faits'] / df['POP']) * 100

    # Vérifier les types de données
    print(df['Code.région'].dtype)  # Afficher le type de données pour le débogage
    print(gdf['code'].dtype)  # Afficher le type de données pour le débogage

    # Convertir les types de données si nécessaire
    df['Code.région'] = df['Code.région'].astype(str)  # Assurez-vous que c'est une chaîne
    gdf['code'] = gdf['code'].astype(str)  # Assurez-vous que c'est une chaîne

    # Fusionner le DataFrame avec le GeoDataFrame sur le code région
    merged = gdf.merge(df, left_on='code', right_on='Code.région', how='left')

    # Vérifier si la géométrie est de type Polygon et obtenir les centroids
    if merged.geometry.geom_type.iloc[0] != 'Point':
        merged['centroid'] = merged.geometry.centroid
        lat = merged.centroid.y
        lon = merged.centroid.x
    else:
        lat = merged.geometry.y
        lon = merged.geometry.x

    min_color = 0
    max_color = 0.6
    # Créer la carte de chaleur
    fig = px.density_mapbox(
        merged,
        lat=lat,
        lon=lon,
        z='pourcentage_criminalite',
        radius=10,
        center=dict(lat=46.6034, lon=1.8883),
        zoom=5,
        mapbox_style="open-street-map",
        color_continuous_scale=px.colors.sequential.Plasma,  # Exemple de palette
        range_color=[min_color, max_color] # Ajustez selon vos données
    )

    # Afficher la carte
    st.plotly_chart(fig)

def dynamic_visualization(df):
    # Streamlit app
    st.title("Visualisation Dynamique des Faits et de la Population")

    # Step 1: Selection of region code
    regions = df['Code.région'].unique()
    selected_region = st.selectbox("Sélectionnez le Code Région", regions)

    # Step 2: Selection of year using a slider
    selected_year = st.slider("Sélectionnez l'âge (Annee)", min_value=int(df['annee'].min()), max_value=int(df['annee'].max()), step=1)

    # Filter the dataset based on selected region and year
    filtered_df = df[(df['Code.région'] == selected_region) & (df['annee'] == selected_year)]

    # Check if the dataframe is empty
    if filtered_df.empty:
        st.write("Pas de données pour cette région et cet âge.")
    else:
        # Step 3: Create the pie chart using 'faits' (a numerical column)
        fig, ax = plt.subplots()

        # Plotting the pie chart with 'faits'
        labels = ['classe']  # Pie chart labels
        sizes = [filtered_df['classe'].values[0]]  # Numerical values for the pie chart

        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)

        # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.axis('equal')  

        # Display the pie chart in Streamlit
        st.pyplot(fig)

        # Step 4: Displaying additional details with a bar chart for 'faits' and line plot for 'millPOP'
        fig, ax = plt.subplots(figsize=(10, 5))

        ax.bar(filtered_df['Code.région'], filtered_df['faits'], color='b', alpha=0.6, label='Faits')
        ax.plot(filtered_df['Code.région'], filtered_df['millPOP'], color='r', marker='o', linestyle='--', label='Population (millPOP)')

        ax.set_title(f"Faits et Population pour l'Age {selected_year} et Région {selected_region}")
        ax.set_xlabel('Code Région')
        ax.set_ylabel('Nombre')
        ax.legend()

        # Display the plot in Streamlit
        st.pyplot(fig)

def dynamic_plot(df):
    # Crée la figure
    fig = go.Figure()

    # Obtenir les années et les régions uniques
    years = sorted(df['annee'].unique())
    regions = df['Code.région'].unique()

    # Ajouter une seule trace pour chaque année
    for year in years:
        # Filtrer les données par année et regrouper les faits par région
        filtered_df = df[df['annee'] == year].groupby('Code.région').agg({'faits': 'sum'}).reset_index()
        filtered_df = filtered_df.sort_values('Code.région')

        # Ajouter une trace pour chaque année
        fig.add_trace(
            go.Scatter(
                visible=False,
                line=dict(color='#4682B4', width=3),
                name=f"Année: {year}",
                x=filtered_df['Code.région'],
                y=filtered_df['faits'],
                mode='lines+markers',
                hovertemplate='Région: %{x}<br>Total des Faits: %{y}'
            )
        )

    # Rendre la première trace visible
    fig.data[0].visible = True

    # Créer et ajouter le slider pour les années
    steps = []
    for i in range(len(fig.data)):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)},
                  {"title": f"Données pour l'année: {years[i]}"}],  # titre du layout
        )
        step["args"][0]["visible"][i] = True  # Rendre la trace i visible
        steps.append(step)

    sliders = [dict(
        active=0,  # Commencer avec la première année
        currentvalue={"prefix": "Année: "},
        pad={"t": 50},
        steps=steps
    )]

    # Mettre à jour le layout avec le slider
    fig.update_layout(
        sliders=sliders,
        title="Visualisation Dynamique des Faits par Région",
        xaxis_title="Code Région",
        yaxis_title="Nombre total de Faits",
        template="plotly_white"
    )

    # Afficher le graphique dans Streamlit
    st.plotly_chart(fig)

def ensemble_viz_faits_region(df):
    # Interface utilisateur dans Streamlit
    st.title('Visualisation du Nombre de Faits et de la Population par Région')
    st.write("Sélectionnez une visualisation :")

    # Agrégation des données : somme des faits pour chaque région et chaque année
    df_agg = df.groupby(['annee', 'Code.région'], as_index=False).agg({
        'faits': 'sum',  # On somme les faits pour chaque région et année
        'POP': 'mean'    # La population reste constante pour chaque région
    })

    # Sélection de l'animation via un bouton radio
    selection = st.radio(
        "Sélectionnez l'animation :",
        ("Faits - Scatter", "Population - Bar", "Graphique")
    )

    # Génération du graphique en fonction de la sélection
    if selection == 'Faits - Scatter':
        fig = px.scatter(
            df_agg, 
            x="Code.région", 
            y="faits", 
            animation_frame="annee", 
            size="faits", 
            color="Code.région", 
            hover_name="Code.région", 
            size_max=20,  # ajustement de la taille maximale pour plus de clarté
            title="Évolution du nombre de faits par région",
            range_y=[0, max(df_agg['faits']) + 10]  # ajustement automatique du range
        )
        st.plotly_chart(fig)
    elif selection == 'Population - Bar':
        fig = px.bar(
            df_agg, 
            x="Code.région", 
            y="faits", 
            color="Code.région", 
            animation_frame="annee", 
            title="Évolution de la population par région",
            range_y=[0, max(df_agg['faits']) + 100000]  # ajustement automatique du range
        )
        st.plotly_chart(fig)
    elif selection == 'Graphique':
        dynamic_plot(df)  # Appeler directement la fonction pour le graphique dynamique







