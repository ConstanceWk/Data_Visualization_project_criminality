import streamlit as st
from functions import *

# In this file we call every functions for the data visualisation

def page_data_visualisation():
    st.title("Communal, departmental and regional statistical bases for delinquency recorded by the national police and gendarmerie")

    try:
        gdf = load_geojson('regions.geojson')
        df = load_data('data_regional.csv')
        
        map_taux_crim(df, gdf)
        print_table(df)
        ensemble_viz_faits_region(df)
        plot_pie_chart(df)
        plot_mapbox(df, gdf)
        plot_3d_barchart_map(df, gdf)
        courbes_vict_mec(df)
        
    except FileNotFoundError:
        st.error("The data file was not found. Please upload a valid CSV file.")

if __name__ == "__main__":
    page_data_visualisation()

