import streamlit as st

st.set_page_config(
    page_title="Coach d'écriture Radio ISTJ",
    page_icon="🎙️"
)

# -----------------------------
# Initialisation de la session
# -----------------------------
if "etape" not in st.session_state:
    st.session_state.etape = "accueil"

if "niveau" not in st.session_state:
    st.session_state.niveau = None

if "nombre_voix" not in st.session_state:
    st.session_state.nombre_voix = None

if "source" not in st.session_state:
    st.session_state.source = ""

# -----------------------------
# Titre
# -----------------------------
st.title("🎙️ Coach d'écriture Radio ISTJ")

# -----------------------------
# ÉTAPE 0 : ACCUEIL
# -----------------------------
if st.session_state.etape == "accueil":

    st.write(
        "Bienvenue dans le Coach d'écriture de Radio ISTJ."
    )

    st.write(
        "Je vais t'aider à préparer ta chronique étape par étape, "
        "sans faire le travail à ta place."
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
            st.session_state.niveau = niveau
            st.session_state.nombre_voix = nombre_voix
            st.session_state.source = source
            st.session_state.etape = "comprehension"

            st.rerun()

# -----------------------------
# ÉTAPE 1 : COMPRÉHENSION
# -----------------------------
elif st.session_state.etape == "comprehension":

    st.subheader("Étape 1 — Comprendre la source")

    st.write(
        f"**Niveau :** {st.session_state.niveau}  \n"
        f"**Format :** {st.session_state.nombre_voix}"
    )

    st.divider()

    sujet = st.text_area(
        "Quel est le sujet principal de l'article ?"
    )

    idees = st.text_area(
        "Quelles sont les 2 ou 3 idées importantes à retenir ?"
    )

    vocabulaire = st.text_area(
        "Y a-t-il un mot ou un passage que tu ne comprends pas ? "
        "Si tout est clair, écris simplement : Aucun."
    )

    if st.button("Continuer"):
        st.info(
            "Très bien. Plus tard, c'est ici que le Coach vérifiera "
            "tes réponses avec l'IA."
        )
