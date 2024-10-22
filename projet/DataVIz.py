import streamlit as st
from functions import *

# In this file we call every functions for the data visualisation

def page_data_visualisation():
    st.title("Regional statistical bases for delinquency recorded by the national police and gendarmerie")

    st.markdown("""
    **Imagine this: in 2022, over 1.5 million crimes were reported in France.** 
    Each statistic tells a story of individuals and communities affected by crime. 
    By exploring regional statistical bases for delinquency recorded by the national police and gendarmerie, 
    I aim to uncover patterns that reveal where help is needed most. 
    Using Streamlit, I want to transform raw data into compelling visuals that not only inform but also drive action. 
    This project is crucial because understanding crime trends can empower us to create safer communities for everyone.
    """)
    
    try:
        gdf = load_geojson('./projet/regions.geojson')
        df = load_data('./projet/data_regional.csv')
        
        print_table(df)
        ensemble_viz_faits_region(df)
        plot_pie_chart(df)
        plot_mapbox(df, gdf)
        plot_3d_barchart_map(df, gdf)
        courbes_vict_mec(df)
        map_taux_crim(df, gdf)
        
    except FileNotFoundError:
        st.error("The data file was not found. Please upload a valid CSV file.")

if __name__ == "__main__":
    page_data_visualisation()

