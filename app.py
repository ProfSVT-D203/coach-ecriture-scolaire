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

            # Une modification des réponses annule l'ancienne analyse.
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
            "La prochaine étape est la vérification de ta compréhension "
            "par le Coach."
        )

        if st.button("Vérifier ma compréhension"):

            try:
                client = OpenAI(
                    api_key=st.secrets["OPENAI_API_KEY"]
                )

                instructions = """
Tu es le Coach d'écriture pédagogique de Radio ISTJ.

Tu vérifies UNIQUEMENT la compréhension d'une source par un élève
de collège.

RÈGLE ABSOLUE :
Tu ne rédiges jamais la chronique à la place de l'élève.
Tu ne fournis jamais une phrase corrigée prête à copier.

OBJECTIF :
Vérifier :
1. si le sujet principal est correctement compris ;
2. si les 2 ou 3 idées choisies par l'élève sont fidèles à la source ;
3. si une idée contient une erreur ou une déformation importante ;
4. si une idée est réellement trop vague pour montrer sa compréhension ;
5. si un mot ou passage signalé comme difficile doit être expliqué.

RÈGLE PRIORITAIRE :
SÉLECTIONNER N'EST PAS DÉFORMER.

Une chronique n'est pas un résumé exhaustif.

L'élève peut sélectionner seulement certaines informations de la source.

Une information exacte ne doit PAS être critiquée simplement :
- parce qu'elle pourrait être plus détaillée ;
- parce que la source contient d'autres informations ;
- parce qu'un terme plus technique ou plus précis existe dans la source ;
- parce qu'un détail supplémentaire pourrait être ajouté.

Ne signale une imprécision que si elle change réellement le sens,
rend l'idée trompeuse ou empêche de comprendre l'information essentielle.

NIVEAU 6e-5e :
- accepte des formulations simples ;
- accepte des reformulations avec les mots de l'élève ;
- n'exige pas de vocabulaire technique inutile ;
- n'exige pas de dates, nombres, lieux, exemples ou détails
  lorsque l'idée essentielle est déjà correcte.

NIVEAU 4e-3e :
- attends davantage de précision et d'explication ;
- mais n'exige jamais l'exhaustivité.

VOCABULAIRE :
Si l'élève signale un mot ou passage incompris,
explique-le simplement et fidèlement à la source.

SI TOUT EST CORRECT :
Réponds exactement :

COMPRÉHENSION VALIDÉE
Tu as bien compris les idées essentielles de la source.
Tu peux passer à la construction du plan.

SI UNE CORRECTION EST NÉCESSAIRE :
Commence exactement par :

À REVOIR

Puis respecte IMPÉRATIVEMENT ces règles :

- commence par dire brièvement ce qui est déjà correct ;
- choisis UNE SEULE difficulté prioritaire ;
- ne corrige pas les petits détails sans conséquence ;
- indique quelle idée pose problème et pourquoi,
  MAIS SANS DONNER L'INFORMATION EXACTE QUI DOIT REMPLACER L'ERREUR ;
- pose UNE SEULE question ciblée permettant à l'élève
  de retrouver lui-même la bonne information dans la source ;
- ne révèle jamais la réponse dans ton explication avant de poser la question ;
- ne cite pas une phrase de la source contenant directement la réponse ;
- ne propose pas de formulation corrigée ;
- ne traite pas plusieurs problèmes à la fois.

EXEMPLE DE COMPORTEMENT INTERDIT :
"L'élève dit que les tissus sont abîmés, mais la source dit
qu'ils sont épargnés. Relis la source : sont-ils touchés ou épargnés ?"

Cet exemple est INTERDIT parce qu'il donne déjà la réponse.

COMPORTEMENT ATTENDU :
"La deuxième idée contient une erreur concernant l'effet du traitement
sur les tissus autour de la tumeur.

Relis le passage qui explique la portée des particules :
que dit-il sur les tissus autour de la tumeur ?"

L'objectif est que l'élève retrouve et formule lui-même la correction.
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

                with st.spinner(
                    "Le Coach vérifie ta compréhension..."
                ):

                    response = client.responses.create(
                        model="gpt-5.6-luna",
                        instructions=instructions,
                        input=input_text
                    )

                st.session_state.feedback_comprehension = (
                    response.output_text
                )

                st.rerun()

            except Exception as e:
                st.error(
                    "Une erreur s'est produite pendant la vérification."
                )
                st.code(str(e))

    else:

        st.subheader("Retour du Coach")

        feedback = st.session_state.feedback_comprehension

        # Affichage plus propre en cas de validation
        if feedback.startswith("COMPRÉHENSION VALIDÉE"):

            st.success("✅ Compréhension validée")

            st.write(
                "Tu as bien compris les idées essentielles de la source."
            )

            st.write(
                "**Étape suivante : construire le plan.**"
            )

        else:

            st.write(feedback)

            st.warning(
                "Corrige tes réponses avant de poursuivre."
            )

            if st.button("Reprendre mes réponses"):
                st.session_state.etape = "comprehension"
                st.rerun()
