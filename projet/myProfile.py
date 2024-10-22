import streamlit as st
from functions import *
# In this page, I have some resume of me with my curriculum
def page_biographie():

    st.title("🌟 My Portfolio - Constance WALUSIAK 🌟")

    st.write("""
    ### Hello and Welcome to My Portfolio! 👋
    I am **Constance WALUSIAK**, and I am excited to share with you a little about myself, my skills, and my data visualisation of the criminality in France. 
    """)
  
    cv_file_path = "./CV_WALUSIAK_CONSTANCE.pdf"  

    with open(cv_file_path, "rb") as cv_file:
        cv_data = cv_file.read()

    st.download_button(
        label="Download my curriculum",
        data=cv_data,
        file_name="Constance_Walusiak_CV.pdf",  
        mime="application/pdf"
    )


    st.write("""
    ## 👩‍💼 About Me
    I am a student in the Data & Artificial Intelligence major. I am passionate about artificial intelligence. In November, I am starting an internship which will allow me to work on a research project related to sport. I will also be present during this internship at the **EFREI Research Lab**. This project allows me to learn more about understanding complex data and creating **interactive visualizations**. 
    I believe that the right information can enable individuals and organizations to make better decisions.

    I thrive in environments that encourage **creative thinking** and problem solving. 💡
             """)


    parcours_aca()
    passions_extra_scolaire()
    repartition_competences()
    wordcloud()
    progression_ia()


    st.sidebar.header("My Skills 💡")
    st.sidebar.write("""
    - 🧠 **Curiosity**: Always eager to learn and explore new things.
    - 🎨 **Innovation**: Bringing creative solutions to real-world problems.
    - 🔥 **Perseverance**: Never give up, always strive for excellence.
    - 💼 **Problem Solving**: Approach challenges with enthusiasm and logic.
    """)


    st.write("""
    ## 📧 Get in Touch!
    Feel free to **reach out** to me if you want to discuss data science! 😊
    Check out my **LinkedIn** profile or send me an **email** 
    """)

    st.write("Thank you for visiting my portfolio! 🙏 ")
