import streamlit as st

st.set_page_config(
    page_title="Coach d'écriture Radio ISTJ",
    page_icon="🎙️"
)

# =========================================================
# INITIALISATION DE LA SESSION
# =========================================================

if "etape" not in st.session_state:
    st.session_state.etape = "accueil"

if "niveau" not in st.session_state:
    st.session_state.niveau = None

if "nombre_voix" not in st.session_state:
    st.session_state.nombre_voix = None

if "source" not in st.session_state:
    st.session_state.source = ""

if "sujet" not in st.session_state:
    st.session_state.sujet = ""

if "idees" not in st.session_state:
    st.session_state.idees = ""

if "vocabulaire" not in st.session_state:
    st.session_state.vocabulaire = ""


# =========================================================
# TITRE
# =========================================================

st.title("🎙️ Coach d'écriture Radio ISTJ")


# =========================================================
# ÉTAPE 0 — ACCUEIL
# =========================================================

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
            st.warning(
                "Tu dois d'abord fournir un article ou une source."
            )

        else:
            st.session_state.niveau = niveau
            st.session_state.nombre_voix = nombre_voix
            st.session_state.source = source

            st.session_state.etape = "comprehension"

            st.rerun()


# =========================================================
# ÉTAPE 1 — COMPRÉHENSION
# =========================================================

elif st.session_state.etape == "comprehension":

    st.subheader("Étape 1 — Comprendre la source")

    st.write(
        f"**Niveau :** {st.session_state.niveau}  \n"
        f"**Format :** {st.session_state.nombre_voix}"
    )

    st.divider()

    sujet = st.text_area(
        "Quel est le sujet principal de l'article ?",
        value=st.session_state.sujet
    )

    idees = st.text_area(
        "Quelles sont les 2 ou 3 idées importantes à retenir ?",
        value=st.session_state.idees,
        height=150
    )

    vocabulaire = st.text_area(
        "Y a-t-il un mot ou un passage que tu ne comprends pas ? "
        "Si tout est clair, écris simplement : Aucun.",
        value=st.session_state.vocabulaire
    )

    if st.button("Continuer"):

        if sujet.strip() == "":
            st.warning(
                "Indique d'abord le sujet principal de l'article."
            )

        elif idees.strip() == "":
            st.warning(
                "Indique au moins les idées importantes que tu as retenues."
            )

        elif vocabulaire.strip() == "":
            st.warning(
                "Indique les mots ou passages difficiles, "
                "ou écris simplement « Aucun »."
            )

        else:
            # Sauvegarde des réponses de l'élève
            st.session_state.sujet = sujet
            st.session_state.idees = idees
            st.session_state.vocabulaire = vocabulaire

            # Passage à l'étape suivante
            st.session_state.etape = "analyse_comprehension"

            st.rerun()


# =========================================================
# ÉTAPE 2 — AVANT ANALYSE IA
# =========================================================

elif st.session_state.etape == "analyse_comprehension":

    st.subheader("Compréhension enregistrée")

    st.success(
        "Tes réponses ont bien été enregistrées."
    )

    st.write("### Sujet principal")
    st.write(st.session_state.sujet)

    st.write("### Idées importantes")
    st.write(st.session_state.idees)

    st.write("### Mots ou passages difficiles")
    st.write(st.session_state.vocabulaire)

    st.divider()

    st.info(
        "La prochaine étape sera la vérification de ta compréhension "
        "par le Coach."
    )

    if st.button("Modifier mes réponses"):
        st.session_state.etape = "comprehension"
        st.rerun()
