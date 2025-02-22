import pandas as pd
from requests import get
from bs4 import BeautifulSoup as bs
import streamlit as st


# Configuration de la page pour une mise en page large et un titre personnalisé
st.set_page_config(
    page_title="Mon App de Scraping",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Injection de CSS personnalisé pour imiter le design souhaité
custom_css = """
<style>
/*Global*/
body {
    background-size: cover;
    background-attachment: fixed;
    background-repeat: no-repeat;
    background-position: center;
    color: #333;
    font-family: 'Segoe UI', sans-serif;
}

/* Header */
h1 {
    font-weight: 700;
    color: #0055AA;
}

/* Sidebar */
.css-1d391kg {  /* classe interne Streamlit susceptible de changer */
    background-color: #FFFFFF;
}

/* Boutons */
.stButton>button {
    background-color: #0066CC;
    color: white;
    border: none;
    padding: 10px 24px;
    border-radius: 4px;
    cursor: pointer;
}
.stButton>button:hover {
    background-color: #0055AA;
}

/* Liens */
a {
    color: #0066CC;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}

/* Iframe responsive */
.responsive-iframe {
    width: 100%;
    height: 500px;
    border: none;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Fonctions de scraping avec BeautifulSoup
# scraping terrains
def scraper_terrains(nb_pages):
    data = []  
    for page in range(1, nb_pages + 1):  # Commencer à la page 1 et inclure nb_pages
        url = f"https://sn.coinafrique.com/categorie/terrains?page={page}"
        res = get(url)
        soup = bs(res.text, 'html.parser')
        containers = soup.find_all('div', class_="col s6 m4 l3")

        for container in containers:
            try:
                url_container_link = 'https://sn.coinafrique.com' + container.find('a', class_='card-image ad__card-image waves-block waves-light')['href']
                res_c = get(url_container_link)
                soup_c = bs(res_c.text, 'html.parser')

                superficie_element = soup_c.find("span", class_="qt")
                superficie = superficie_element.text.strip().replace("m2", '') if superficie_element else None

                prix_element = soup_c.find("p", class_="price")
                prix = prix_element.text.replace(' ', '').replace("CFA", '') if prix_element else None

                gen_inf = soup_c.find_all('span', class_='valign-wrapper')
                adresse = ", ".join([info.text for info in gen_inf[1:]])
                adresse = adresse.rstrip(", ").replace(", ", '  ')
                adresse = '  '.join(adresse.split('  ')[:2])  # Garder seulement les deux premières parties

                img_link = 'https://sn.coinafrique.com' + container.find('img', class_='ad__card-img')['src']
                dic = {"Superficie": superficie, "Prix": prix, "Adresse": adresse, "Image": img_link}
                data.append(dic)
            except Exception as e:
                print(f"Erreur lors du scraping : {e}")

    return pd.DataFrame(data)

# scraping appartements
def scraper_appartements(nb_pages):
    data = [] 
    for page in range(1, nb_pages + 1):  # Commencer à la page 1 et inclure nb_pages
        url = f"https://sn.coinafrique.com/categorie/appartements?page={page}"
        res = get(url)
        soup = bs(res.text, 'html.parser')
        containers = soup.find_all('div', class_="col s6 m4 l3")

        for container in containers:
            try:
                url_container_link = 'https://sn.coinafrique.com' + container.find('a', class_='card-image ad__card-image waves-block waves-light')['href']
                res_c = get(url_container_link)
                soup_c = bs(res_c.text, 'html.parser')

                pieces_element = soup_c.find("span", class_="qt")
                pieces = pieces_element.text.strip().replace(" ", '') if pieces_element else None

                prix_element = soup_c.find("p", class_="price")
                prix = prix_element.text.replace(' ', '').replace("CFA", '') if prix_element else None

                gen_inf = soup_c.find_all('span', class_='valign-wrapper')
                adresse = ", ".join([info.text for info in gen_inf[1:]])
                adresse = adresse.rstrip(", ").replace(", ", '  ')
                adresse = '  '.join(adresse.split('  ')[:2])  # Garder seulement les deux premières parties

                img_link = 'https://sn.coinafrique.com' + container.find('img', class_='ad__card-img')['src'] if container.find('img', class_='ad__card-img') else None
                dic = {"Nombre de pièces": pieces, "Prix": prix, "Adresse": adresse, "Image": img_link}
                data.append(dic)
            except Exception as e:
                print(f"Erreur lors du scraping : {e}")

    return pd.DataFrame(data)

def main():
    # Titre de l'app
    st.title("Application de Scraping et d'Évaluation")
    # description et sources des donnees
    st.markdown("""
    Cette application permet de scrapper mais aussi de recolter  les avis en rapport avec la vente des terrains et des appartements à Dakar
    * **Python libraries:**  pandas, streamlit, requests, bs4
    * **Data source:** [Terrains](https://sn.coinafrique.com/categorie/terrains  ) -- [Appartements](https://sn.coinafrique.com/categorie/appartements ).
    """)

    # Menu latéral de navigation
    st.sidebar.header("Menu")
    choix = st.sidebar.radio(
        "Sélectionnez une action :",
        [
            "Scraper avec BeautifulSoup",
            "Télécharger données Web Scraper",
            "Formulaire d'évaluation Kobo",
            "Formulaire d'évaluation Google Forms"
        ]
    )

   # 1. Scraping avec BeautifulSoup
    if choix == "Scraper avec BeautifulSoup":
        st.header("Scraper et nettoyer les données avec BeautifulSoup")
        categorie = st.selectbox("Choisissez la catégorie :", ["Terrains", "Appartements"])
        nb_pages = st.number_input("Nombre de pages à scraper :", min_value=1, max_value=119, value=1)
        if st.button("Lancer le scraping"):
            with st.spinner("Scraping en cours..."):
                if categorie == "Terrains":
                    df = scraper_terrains(nb_pages)
                else:
                    df = scraper_appartements(nb_pages)
            st.success("Scraping terminé !")
            st.write(f"Taille de la table: {df.shape[0]} lignes et {df.shape[1]} colonnes")
            df.index = [f"E{i+1}" for i in range(len(df))]
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=True).encode("utf-8")
            st.download_button(
                label="Télécharger les données",
                data=csv,
                file_name=f"{categorie.lower()}_scrape.csv",
                mime="text/csv"
            )

    # 2. Téléchargement des données issues du Web Scraper (non nettoyées)
    elif choix == "Télécharger données Web Scraper":
        st.header("Données Web Scraper (non nettoyées)")

        # Permettre à l'utilisateur de choisir entre Terrains et Appartements
        categorie = st.selectbox("Choisissez la catégorie :", ["Terrains", "Appartements"])

        # Définir le chemin vers le fichier CSV selon la catégorie choisie
        if categorie == "Terrains":
            file_path = "data/terrains.csv"
        else:
            file_path = "data/apparts.csv"

        try:
            # Charger le fichier CSV localement
            df_web = pd.read_csv(file_path)
            st.dataframe(df_web, use_container_width=True)

            # Préparer le CSV pour le téléchargement
            csv = df_web.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Télécharger le fichier",
                data=csv,
                file_name=file_path.split("/")[-1],
                mime="text/csv"
            )
        except FileNotFoundError as e:  # More specific exception handling
            st.error(f"Fichier non trouvé : {file_path}. Veuillez vérifier le chemin.")
        except Exception as e:
            st.error("Erreur lors de la lecture du fichier : " + str(e))

    # 3. Formulaire d'évaluation via Kobo
    elif choix == "Formulaire d'évaluation Kobo":
        st.header("Évaluation de l'application (Kobo)")
        # Remplacez l'URL par celle de votre formulaire Kobo
        kobo_form_url = "https://ee.kobotoolbox.org/i/y3pfGxMz"
        st.markdown(
            f"""
            <iframe class="responsive-iframe" src="{kobo_form_url}"></iframe>
            """,
            unsafe_allow_html=True
        )

    # 4. Formulaire d'évaluation via Google Forms
    elif choix == "Formulaire d'évaluation Google Forms":
        st.header("Évaluation de l'application (Google Forms)")
        # Remplacez l'URL par celle de votre Google Form
        google_form_url = "https://forms.gle/YccYeHJd7ojoPFp67"
        st.markdown(
            f"""
            <iframe class="responsive-iframe" src="{google_form_url}"></iframe>
            """,
            unsafe_allow_html=True
        )

if __name__ == '__main__':
    main()
