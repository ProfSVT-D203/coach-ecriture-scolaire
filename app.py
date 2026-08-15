import streamlit as st
from openai import OpenAI

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

if "feedback_comprehension" not in st.session_state:
    st.session_state.feedback_comprehension = ""


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
            st.session_state.sujet = sujet
            st.session_state.idees = idees
            st.session_state.vocabulaire = vocabulaire
            st.session_state.feedback_comprehension = ""

            st.session_state.etape = "analyse_comprehension"

            st.rerun()


# =========================================================
# ÉTAPE 2 — VÉRIFICATION DE LA COMPRÉHENSION
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

    if st.button("Modifier mes réponses"):
        st.session_state.etape = "comprehension"
        st.rerun()

    st.divider()

    if st.session_state.feedback_comprehension == "":

        st.info(
            "La prochaine étape est la vérification de ta compréhension par le Coach."
        )

        if st.button("Vérifier ma compréhension"):

            try:
                client = OpenAI(
                    api_key=st.secrets["OPENAI_API_KEY"]
                )

                instructions = """
Tu es le Coach d'écriture pédagogique de Radio ISTJ.

Tu vérifies uniquement l'étape de compréhension d'un élève de collège
à partir de la source fournie.

RÈGLE FONDAMENTALE :
Tu ne rédiges jamais la chronique à la place de l'élève.

Tu dois vérifier :
1. si le sujet principal est correctement compris ;
2. si chacune des 2 ou 3 idées importantes est fidèle à la source ;
3. si une idée contient une erreur ou une imprécision factuelle importante ;
4. si les difficultés de vocabulaire signalées doivent être expliquées.

RÈGLE PRIORITAIRE :
Sélectionner n'est pas déformer.

L'élève n'a pas besoin de reprendre toutes les informations de la source.
Si une idée choisie est exacte, ne la considère pas comme insuffisante
simplement parce que la source contient davantage de détails.

Distingue absolument :
- une information fausse ou déformée ;
- une information correcte mais sélectionnée ;
- une information réellement trop vague pour montrer que l'idée est comprise.

Pour un élève de niveau 6e-5e :
- accepte des formulations simples ;
- accepte une sélection de 2 ou 3 idées essentielles ;
- n'exige pas des nombres, dates, exemples ou détails inutiles
  si l'idée est déjà comprise.

Pour un élève de niveau 4e-3e :
- attends davantage de précision et d'explication ;
- mais n'exige jamais l'exhaustivité de la source.

Si un mot ou un passage est signalé comme incompris :
- explique-le simplement avec un vocabulaire adapté au niveau ;
- reste fidèle au sens qu'il possède dans la source.

Si une réponse doit être corrigée :
- indique ce qui est déjà correct ;
- identifie UNE seule difficulté prioritaire ;
- pose UNE question ciblée qui aide l'élève à retrouver lui-même
  l'information dans la source ;
- ne donne pas directement la réponse si elle peut être retrouvée dans la source ;
- ne propose jamais une phrase prête à copier.

Si toutes les réponses montrent une compréhension suffisante,
réponds exactement :

COMPRÉHENSION VALIDÉE
Tu as bien compris les idées essentielles de la source.
Tu peux passer à la construction du plan.

Sinon, commence exactement par :

À REVOIR

Puis donne un retour court et adapté à un collégien.
"""

                input_text = f"""
NIVEAU DE L'ÉLÈVE :
{st.session_state.niveau}

SOURCE :
{st.session_state.source}

RÉPONSE DE L'ÉLÈVE — SUJET PRINCIPAL :
{st.session_state.sujet}

RÉPONSE DE L'ÉLÈVE — IDÉES IMPORTANTES :
{st.session_state.idees}

RÉPONSE DE L'ÉLÈVE — MOTS OU PASSAGES DIFFICILES :
{st.session_state.vocabulaire}
"""

                with st.spinner("Le Coach vérifie ta compréhension..."):

                    response = client.responses.create(
                        model="gpt-5.6-luna",
                        instructions=instructions,
                        input=input_text
                    )

                st.session_state.feedback_comprehension = response.output_text
                st.rerun()

            except Exception as e:
                st.error(
                    "Une erreur s'est produite pendant la vérification."
                )
                st.code(str(e))

    else:

        st.subheader("Retour du Coach")

        st.write(
            st.session_state.feedback_comprehension
        )

        if st.session_state.feedback_comprehension.startswith(
            "COMPRÉHENSION VALIDÉE"
        ):
            st.success(
                "La compréhension est validée."
            )

        else:
            st.warning(
                "Corrige tes réponses avant de poursuivre."
            )

            if st.button("Reprendre mes réponses"):
                st.session_state.etape = "comprehension"
                st.rerun()
