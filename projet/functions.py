import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from functions import *
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import numpy as np
from wordcloud import WordCloud


# ------------------ VISUALISATION OF MY DATASET -------------------- #

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
   
    st.header("Pie chart view of facts by region")
    
    classe_selected = st.selectbox("Select the fact of the crime :", df['classe'].unique())
    filtered_data = df[df['classe'] == classe_selected]
    data_grouped = filtered_data.groupby('Code.région')['faits'].sum().reset_index()
    fig = px.pie(data_grouped, names='Code.région', values='faits', 
                 title=f"Distribution of facts for the class '{classe_selected}'")

    st.plotly_chart(fig)
    st.markdown("""
    We can take an example of homicides. **Aude**, **Seine-Saint-Denis**, and **Vaucluse** have reported significant incidents of homicide, 
    raising concerns about safety and community well-being. These areas face unique challenges that may 
    contribute to higher crime rates, including socio-economic factors and urban dynamics. 
    Understanding the specific context of these regions is crucial for developing effective strategies 
    to combat violence and support affected communities. By analyzing these trends, we can work towards 
    a safer environment for all residents.
    """)

def plot_mapbox(df, gdf):
    
    st.header("Interactive crime map of France (using Mapbox)")
    classe_selected = st.selectbox("Select the fact:", df['classe'].unique())
 
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
        title=f"Distribution of facts for the crime :'{classe_selected}'"
    )
  
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig)

    st.markdown("""
    The interactive map of crimes uses a color gradient from violet to yellow, 
    where the intensity of yellow indicates a higher prevalence of crime. 
    As you explore the map, we can say that **Île-de-France** is the most affected region, 
    marked by deeper shades of yellow. This visualization not only highlights the areas 
    most impacted by crime but also serves as a critical tool for understanding regional disparities. 
    """)

def plot_3d_barchart_map(df, gdf):
    st.header("Interactive map with distinct 3D bars for each facts")

    if not isinstance(gdf, gpd.GeoDataFrame):
        gdf = gpd.GeoDataFrame(gdf, geometry=gpd.GeoSeries(gdf['geometry']))
  
    df['Code.région'] = df['Code.région'].astype(str)
    gdf['region_code'] = gdf['code'].astype(str)

    merged_data = pd.merge(df, gdf[['region_code', 'geometry']], 
                           left_on='Code.région', right_on='region_code', how='left')

    merged_data = gpd.GeoDataFrame(merged_data, geometry='geometry')

    fig = go.Figure()

    colors = px.colors.qualitative.Plotly
    classes = df['classe'].unique()

    offset = 0.02

    for i, classe in enumerate(classes):
        classe_data = merged_data[merged_data['classe'] == classe]

        x = classe_data['geometry'].centroid.x.tolist()
        y = classe_data['geometry'].centroid.y.tolist()
        z = np.zeros(len(classe_data)).tolist() 
        dz = classe_data['faits'].tolist()  

        x_offset = [xi + (i * offset) for xi in x] 
        y_offset = [yi + (i * offset) for yi in y]  
      
        for j in range(len(x)):

            name = classe if j == 0 else None
            fig.add_trace(go.Scatter3d(
                x=[x_offset[j], x_offset[j], x_offset[j]],  
                y=[y_offset[j], y_offset[j], y_offset[j]], 
                z=[0, dz[j], 0], 
                mode='lines',
                line=dict(color=colors[i % len(colors)], width=6),  
                name=name,  
                showlegend=name is not None, 
                hoverinfo='text',  
                hovertext=classe 
            ))

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
    
 
    fig.update_layout(
        scene=dict(
            xaxis_title='Longitude',
            yaxis_title='Latitude',
            zaxis_title='Nombre de faits',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
        ),
        margin=dict(r=0, t=0, l=0, b=0),
        showlegend=True
    )

    st.plotly_chart(fig)
    st.markdown("""
    This analysis aims to understand and visualize the significance and alarming numbers associated with different types of crimes. 
    In particular, we observe that **Île-de-France** stands out with a staggering number of incidents categorized as "theft without violence against individuals." 
    This type of crime significantly outnumbers other offenses, highlighting the urgent need for attention and intervention in this area. 
    By breaking down crime statistics by type, we can better comprehend the challenges faced by communities and develop tailored strategies to address these pressing issues.
    """)

def courbes_vict_mec(df):
    st.header("Distribution of victims / implicated parties")
    df_victimes = df[df['unité.de.compte'] == 'victime']
    df_mis_en_cause = df[df['unité.de.compte'] == 'Mis en cause']

    fig_victimes = px.bar(df_victimes, 
                          x='Code.région', 
                          y='faits', 
                          color='classe', 
                          title='Facts suffered by the victims',
                          labels={'Code.région': 'Code de région', 'faits': 'Nombre de faits'},
                          text='faits')
    
    st.plotly_chart(fig_victimes)

    fig_mis_en_cause = px.bar(df_mis_en_cause, 
                              x='Code.région', 
                              y='faits', 
                              color='classe', 
                              title='Facts performed by the accused',
                              labels={'Code.région': 'Code de région', 'faits': 'Nombre de faits'},
                              text='faits')

    st.plotly_chart(fig_mis_en_cause)
    st.markdown("""
    In this analysis, I have separated the data into two distinct graphs: one for the **accused** and another for the **victims** in relation to the crimes committed. 
    The data reveals a concerning trend: individuals recorded as victims have suffered from various serious offenses, including homicides, 
    voluntary assaults, intra-family voluntary assaults, other voluntary assaults, sexual violence, and fraud. 
    These categories highlight the severity and variety of crimes impacting victims in our dataset.

    On the other hand, the accused individuals in our dataset are predominantly recorded for drug trafficking and drug use offenses. 
    This stark contrast between the types of crimes associated with victims and those linked to the accused raises important questions 
    about the nature of violence and crime within our communities.

    Moreover, it is crucial to note that the dataset does not capture all incidents, leaving gaps in our understanding of crime dynamics. 
    This incomplete representation may affect our conclusions and highlights the need for comprehensive data collection to fully understand 
    the complexities surrounding crime and victimization in society.
    """)

def map_taux_crim(df, gdf):
    st.header("Map with Crime rate.")
    df['pourcentage_criminalite'] = (df['faits'] / df['POP']) * 100

    df['Code.région'] = df['Code.région'].astype(str)
    gdf['code'] = gdf['code'].astype(str)

    merged = gdf.merge(df, left_on='code', right_on='Code.région', how='left')

    if merged.geometry.geom_type.iloc[0] != 'Point':
        merged['centroid'] = merged.geometry.centroid
        lat = merged.centroid.y
        lon = merged.centroid.x
    else:
        lat = merged.geometry.y
        lon = merged.geometry.x

    fig = px.scatter_mapbox(
        merged,
        lat=lat,
        lon=lon,
        size='pourcentage_criminalite', 
        color='pourcentage_criminalite',  
        color_continuous_scale=px.colors.sequential.Viridis,  
        size_max=15,  
        zoom=5,
        mapbox_style="open-street-map",
        range_color=[0, 2]  
    )

    st.plotly_chart(fig)

    st.markdown("""
    The crime rate map visually represents the levels of criminal activity across different regions, utilizing a color gradient 
    that ranges from violet to yellow. In this map, deeper shades of yellow indicate higher crime rates, with some areas 
    reaching an alarming **0.70% crime rate** in the vicinity of Paris. 

    This visualization effectively highlights regions that are more affected by crime, allowing us to pinpoint areas 
    that may require enhanced security measures and community support. By understanding the distribution of crime rates, 
    we can better address the underlying issues contributing to these statistics and work towards fostering safer communities 
    for all residents.
    """)

def dynamic_visualization(df):
    st.header("Pie chart view of facts by region")

    regions = df['Code.région'].unique()
    selected_region = st.selectbox("Select the region", regions)

    selected_year = st.slider("Sélectionnez l'âge (Annee)", min_value=int(df['annee'].min()), max_value=int(df['annee'].max()), step=1)

    filtered_df = df[(df['Code.région'] == selected_region) & (df['annee'] == selected_year)]

    if filtered_df.empty:
        st.write("Pas de données pour cette région et cet âge.")
    else:
        fig, ax = plt.subplots()
        labels = ['classe']  
        sizes = [filtered_df['classe'].values[0]] 

        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  
        st.pyplot(fig)
        fig, ax = plt.subplots(figsize=(10, 5))

        ax.bar(filtered_df['Code.région'], filtered_df['faits'], color='b', alpha=0.6, label='Faits')
        ax.plot(filtered_df['Code.région'], filtered_df['millPOP'], color='r', marker='o', linestyle='--', label='Population (millPOP)')

        ax.set_title(f"Faits et Population pour l'Age {selected_year} et Région {selected_region}")
        ax.set_xlabel('Code Région')
        ax.set_ylabel('Nombre')
        ax.legend()
        st.pyplot(fig)

def dynamic_plot(df):
   
    fig = go.Figure()

    years = sorted(df['annee'].unique())
    regions = df['Code.région'].unique()

    for year in years:
        filtered_df = df[df['annee'] == year].groupby('Code.région').agg({'faits': 'sum'}).reset_index()
        filtered_df = filtered_df.sort_values('Code.région')

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

    fig.data[0].visible = True

    steps = []
    for i in range(len(fig.data)):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)},
                  {"title": f"Data for the year: {years[i]}"}],  
        )
        step["args"][0]["visible"][i] = True
        steps.append(step)

    sliders = [dict(
        active=0, 
        currentvalue={"prefix": "Année: "},
        pad={"t": 50},
        steps=steps
    )]

    fig.update_layout(
        sliders=sliders,
        xaxis_title="Code Région",
        yaxis_title="Number of Crimes",
        template="plotly_white"
    )

    st.plotly_chart(fig)

def ensemble_viz_faits_region(df):
    
    st.header('Visualization of the number of crimes in each region by age')

    st.markdown("""
    The analysis of crime rates by age across different regions reveals a notable consistency. 
    While we observe a steady trend in the number of incidents among various age groups, 
    there is a slight spike at the age of 20. This small variation could indicate 
    a unique set of circumstances that affect this age group, possibly linked to 
    social and economic factors that lead to higher crime rates during early adulthood. 
    Understanding these dynamics is essential for crafting targeted interventions that address 
    the root causes of delinquency, ultimately fostering safer communities for all.
    """)
    df_agg = df.groupby(['annee', 'Code.région'], as_index=False).agg({
        'faits': 'sum',  
        'POP': 'mean'  
    })

    selection = st.radio(
        "Select the visualization :",
        ("Scatter", "Bar", "Chart")
    )

    if selection == 'Scatter':
        fig = px.scatter(
            df_agg, 
            x="Code.région", 
            y="faits", 
            animation_frame="annee", 
            size="faits", 
            color="Code.région", 
            hover_name="Code.région", 
            size_max=20, 
            range_y=[0, max(df_agg['faits']) + 10]
        )
        st.plotly_chart(fig)
    elif selection == 'Bar':
        fig = px.bar(
            df_agg, 
            x="Code.région", 
            y="faits", 
            color="Code.région", 
            animation_frame="annee", 
            range_y=[0, max(df_agg['faits']) + 100000] 
        )
        st.plotly_chart(fig)
    elif selection == 'Chart':
        dynamic_plot(df)  

# ------------------ MY PROFIL -------------------- #


def parcours_aca():
    data_gantt = {
    'Task': ["High School: L'Espérance", "EFREI Paris", "Internship M1: Innowide", "Internship M2: ???"],
    'Début': ["2018-09-01", "2021-09-01", "2024-11-04", "2026-04-01"],
    'Fin': ["2021-06-30", "2026-06-30", "2025-03-28", "2026-08-30"],
    'Couleur': ['#FF6347', '#1E90FF', '#32CD32', '#FFD700']
    }

    df_gantt = pd.DataFrame(data_gantt)

    
    fig_gantt = px.timeline(df_gantt, x_start="Début", x_end="Fin", y="Task",
                            title="My Academic Background",
                            color='Task',  
                            color_discrete_sequence=df_gantt['Couleur'])  

    fig_gantt.update_yaxes(categoryorder="total ascending")  
    fig_gantt.update_xaxes(type='date')

    st.plotly_chart(fig_gantt)

def repartition_competences():
   
    data_competences = {
        'Compétences': ['Python', 'Machine Learning', 'Data Visualization', 'Database'],
        'Pourcentage': [40, 30, 30, 20]
    }

    df_competences = pd.DataFrame(data_competences)

    fig_pie = px.pie(df_competences, names='Compétences', values='Pourcentage',
                    title="A little more about my technical skills ...")

    st.plotly_chart(fig_pie)

def wordcloud():

    texte_interets = """
    Sport, Intelligence Artificielle, Visualisation de données, Recherche, Technologie Générative, Projets, Innovation
    """

    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(texte_interets)

    st.write("My interests (using wordCloud)")
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)

def progression_ia():
    data_progression = {
        'Année': [ 2022, 2023, 2024, 2025],
        'project': [1, 3, 4, 4]
    }

    df_progression = pd.DataFrame(data_progression)

    fig_progression = px.line(df_progression, x='Année', y='project',
                            title="Progress of my AI projects",
                            markers=True)

    st.plotly_chart(fig_progression)

def passions_extra_scolaire():
    data_passions = {
        'Activités': ['Sport', 'Couture', 'Crochet', 'Peinture', 'Cuisine'],
        'Engagement': [80, 60, 70, 50, 90] 
    }

    df_passions = pd.DataFrame(data_passions)

    fig_radar = px.line_polar(df_passions, r='Engagement', theta='Activités', 
                              line_close=True, title="My passions outside school", 
                              range_r=[0, 100], 
                              color_discrete_sequence=['#FF6347'])

    fig_radar.update_traces(fill='toself')

    st.plotly_chart(fig_radar)


