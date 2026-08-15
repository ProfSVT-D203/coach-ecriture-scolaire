import streamlit as st

st.set_page_config(
    page_title="Coach d'écriture Radio ISTJ",
    page_icon="🎙️"
)

st.title("🎙️ Coach d'écriture Radio ISTJ")

st.write(
    "Bienvenue dans le Coach d'écriture de Radio ISTJ."
)

st.write(
    "Je vais t'aider à préparer ta chronique étape par étape, sans faire le travail à ta place."
)

st.divider()

niveau = st.radio(
    "Quel est ton niveau ?",
    ["6e-5e", "4e-3e"]
)

nombre_voix = st.radio(
    "Combien de voix pour la chronique ?",
    ["1 voix", "2 voix", "3 voix"]
)

source = st.text_area(
    "Colle ici l'article ou la source utilisée pour préparer ta chronique :",
    height=300
)

if st.button("Commencer"):
    if source.strip() == "":
        st.warning("Tu dois d'abord fournir un article ou une source.")
    else:
        st.success("La source a bien été enregistrée.")

        st.write(f"**Niveau choisi :** {niveau}")
        st.write(f"**Format choisi :** {nombre_voix}")

        st.info("Étape suivante : vérifier la compréhension de la source.")
