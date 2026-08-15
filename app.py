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

if "plan_introduction" not in st.session_state:
    st.session_state.plan_introduction = ""

if "plan_developpement" not in st.session_state:
    st.session_state.plan_developpement = ""

if "plan_conclusion" not in st.session_state:
    st.session_state.plan_conclusion = ""

if "plan_repartition" not in st.session_state:
    st.session_state.plan_repartition = ""

if "feedback_plan" not in st.session_state:
    st.session_state.feedback_plan = ""


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

        if feedback.startswith("COMPRÉHENSION VALIDÉE"):

            st.success("✅ Compréhension validée")

            st.write(
                "Tu as bien compris les idées essentielles de la source."
            )

            st.write(
                "**Étape suivante : construire le plan.**"
            )

            if st.button("Construire mon plan"):
                st.session_state.etape = "plan"
                st.rerun()

        else:

            st.write(feedback)

            st.warning(
                "Corrige tes réponses avant de poursuivre."
            )

            if st.button("Reprendre mes réponses"):
                st.session_state.etape = "comprehension"
                st.rerun()


# =========================================================
# ÉTAPE 3 — CONSTRUCTION DU PLAN
# =========================================================

elif st.session_state.etape == "plan":

    st.subheader("Étape 2 — Construire le plan")

    st.write(
        "Avant d'écrire la chronique, organise les idées que tu veux présenter."
    )

    st.write(
        "Le plan indique ce que chaque partie doit expliquer. "
        "Tu n'as pas encore besoin d'écrire les phrases de la chronique."
    )

    st.divider()

    st.write(
        f"**Niveau :** {st.session_state.niveau}  \n"
        f"**Format :** {st.session_state.nombre_voix}"
    )

    st.divider()

    plan_introduction = st.text_area(
        "Introduction — Que veux-tu présenter au début de la chronique ?",
        value=st.session_state.plan_introduction,
        height=100
    )

    plan_developpement = st.text_area(
        "Développement — Quelles idées veux-tu expliquer, et dans quel ordre ?",
        value=st.session_state.plan_developpement,
        height=180
    )

    plan_conclusion = st.text_area(
        "Conclusion — Sur quelle idée veux-tu terminer la chronique ?",
        value=st.session_state.plan_conclusion,
        height=100
    )

    if st.session_state.nombre_voix in ["2 voix", "3 voix"]:

        st.divider()

        if st.session_state.nombre_voix == "2 voix":
            texte_repartition = (
                "Répartition des 2 voix — "
                "Comment allez-vous répartir les différentes parties "
                "entre la voix 1 et la voix 2 ?"
            )
        else:
            texte_repartition = (
                "Répartition des 3 voix — "
                "Comment allez-vous répartir les différentes parties "
                "entre les voix 1, 2 et 3 ?"
            )

        plan_repartition = st.text_area(
            texte_repartition,
            value=st.session_state.plan_repartition,
            height=150
        )

    else:
        plan_repartition = ""

    st.divider()

    if st.button("Enregistrer mon plan"):

        if plan_introduction.strip() == "":
            st.warning(
                "Indique ce que tu veux présenter dans l'introduction."
            )

        elif plan_developpement.strip() == "":
            st.warning(
                "Indique les idées que tu veux expliquer dans le développement."
            )

        elif plan_conclusion.strip() == "":
            st.warning(
                "Indique sur quelle idée tu veux terminer."
            )

        elif (
            st.session_state.nombre_voix in ["2 voix", "3 voix"]
            and plan_repartition.strip() == ""
        ):
            st.warning(
                "Indique comment les prises de parole seront réparties."
            )

        else:
            st.session_state.plan_introduction = plan_introduction
            st.session_state.plan_developpement = plan_developpement
            st.session_state.plan_conclusion = plan_conclusion
            st.session_state.plan_repartition = plan_repartition

            # Si le plan est modifié, une ancienne validation
            # ne doit pas être conservée.
            st.session_state.feedback_plan = ""

            st.session_state.etape = "plan_enregistre"

            st.rerun()


# =========================================================
# ÉTAPE 4 — PLAN ENREGISTRÉ + VÉRIFICATION IA
# =========================================================

elif st.session_state.etape == "plan_enregistre":

    st.subheader("Plan enregistré")

    st.success(
        "Ton plan a bien été enregistré."
    )

    st.write("### Introduction")
    st.write(st.session_state.plan_introduction)

    st.write("### Développement")
    st.write(st.session_state.plan_developpement)

    st.write("### Conclusion")
    st.write(st.session_state.plan_conclusion)

    if st.session_state.nombre_voix in ["2 voix", "3 voix"]:

        st.write("### Répartition des voix")
        st.write(st.session_state.plan_repartition)

    st.divider()

    if st.button("Modifier mon plan"):
        st.session_state.etape = "plan"
        st.rerun()

    st.divider()

    # -----------------------------------------------------
    # LE PLAN N'A PAS ENCORE ÉTÉ VÉRIFIÉ
    # -----------------------------------------------------

    if st.session_state.feedback_plan == "":

        st.info(
            "La prochaine étape est la vérification du plan par le Coach."
        )

        if st.button("🤖 Faire vérifier mon plan par le Coach"):

            try:

                client = OpenAI(
                    api_key=st.secrets["OPENAI_API_KEY"]
                )

                instructions_plan = """
Tu es le Coach d'écriture pédagogique de Radio ISTJ.

Tu vérifies UNIQUEMENT le PLAN préparé par un élève de collège
avant la rédaction d'une chronique radio.

RÈGLE ABSOLUE :
Tu ne rédiges jamais la chronique à la place de l'élève.
Tu ne transformes pas son plan en phrases prêtes à être utilisées.
Tu ne proposes pas un nouveau plan complet à sa place.

Le plan n'est PAS la chronique.
Il peut être écrit sous forme de notes, de groupes de mots
ou de phrases très simples.

OBJECTIF :
Vérifier si le plan permet à l'élève de commencer ensuite la rédaction.

Le plan doit comporter :
1. une introduction qui permet d'identifier suffisamment le sujet ;
2. un développement organisé autour des idées que l'élève
   a choisi de retenir ;
3. une conclusion cohérente avec le sujet ;
4. pour une chronique à plusieurs voix, une répartition
   suffisamment claire des prises de parole.

RÈGLE PRIORITAIRE :
SÉLECTIONNER N'EST PAS DÉFORMER.

Une chronique radio n'est pas un résumé exhaustif de la source.

L'élève n'a PAS à reprendre toutes les informations de l'article.

Si la source présente plusieurs causes, conséquences, exemples,
résultats ou explications, l'élève peut n'en sélectionner qu'une partie,
à condition que les informations retenues soient exactes
et qu'il ne fasse pas croire qu'elles sont les seules.

Ne demande donc PAS d'ajouter une information simplement parce que :
- elle existe dans la source ;
- elle apporterait davantage de détails ;
- elle rendrait la chronique plus complète ;
- elle permettrait d'utiliser un terme plus technique.

FIDÉLITÉ :
Une information du plan doit être signalée seulement si :
- elle est fausse ;
- elle déforme réellement la source ;
- elle inverse une relation importante ;
- elle affirme quelque chose que la source ne permet pas d'affirmer.

INTRODUCTION :
L'introduction doit permettre d'identifier suffisamment le sujet
et de comprendre pourquoi il mérite une chronique.

Pour un élève de 6e-5e :
- une ou deux idées simples peuvent suffire ;
- n'exige pas systématiquement une date ;
- n'exige pas systématiquement un chiffre ;
- n'exige pas systématiquement un lieu plus précis ;
- n'exige pas systématiquement une cause ;
- n'exige pas systématiquement un exemple ;
- n'exige pas systématiquement un détail technique.

Pour un élève de 4e-3e :
- attends davantage de précision et d'organisation ;
- mais n'exige jamais l'exhaustivité.

DÉVELOPPEMENT :
Vérifie surtout :
- que les idées prévues sont compréhensibles ;
- qu'elles sont compatibles avec la source ;
- qu'il existe un ordre exploitable pour la rédaction.

Ne demande pas d'ajouter toutes les idées importantes identifiées
pendant l'étape de compréhension.
L'élève reste libre de sélectionner les informations qu'il utilisera.

CONCLUSION :
Elle peut être courte.
Elle doit simplement permettre de terminer la chronique
de manière cohérente.

Ne demande pas une ouverture artificielle ou une nouvelle information
si la conclusion prévue remplit déjà cette fonction.

PLUSIEURS VOIX :
Pour 2 ou 3 voix, vérifie seulement que la répartition permet
de comprendre qui intervient dans les différentes parties.

N'exige pas une alternance parfaite entre les voix.
N'exige pas que toutes les voix parlent exactement autant.
N'exige pas encore les phrases du dialogue.

SI LE PLAN EST SUFFISANT :
Réponds exactement :

PLAN VALIDÉ
Ton plan est suffisamment clair et organisé.
Tu peux commencer la rédaction de l'introduction.

SI UNE CORRECTION EST RÉELLEMENT NÉCESSAIRE :
Commence exactement par :

À REVOIR

Puis :

- commence par dire brièvement ce qui fonctionne déjà ;
- choisis UNE SEULE difficulté prioritaire ;
- explique le type de problème sans écrire la correction ;
- pose UNE SEULE question ciblée pour aider l'élève
  à améliorer lui-même son plan ;
- ne donne jamais un plan corrigé ;
- ne donne jamais une phrase prête à copier ;
- ne traite pas plusieurs problèmes à la fois.

IMPORTANT :
Un plan simple mais correct doit être validé.
Ne surcorrige pas.
"""

                input_plan = f"""
NIVEAU :
{st.session_state.niveau}

FORMAT :
{st.session_state.nombre_voix}

SOURCE :
{st.session_state.source}

COMPRÉHENSION DÉJÀ VALIDÉE PAR LE COACH :

SUJET PRINCIPAL :
{st.session_state.sujet}

IDÉES IMPORTANTES RETENUES PAR L'ÉLÈVE :
{st.session_state.idees}

PLAN PROPOSÉ PAR L'ÉLÈVE :

INTRODUCTION :
{st.session_state.plan_introduction}

DÉVELOPPEMENT :
{st.session_state.plan_developpement}

CONCLUSION :
{st.session_state.plan_conclusion}

RÉPARTITION DES VOIX :
{st.session_state.plan_repartition}
"""

                with st.spinner(
                    "Le Coach vérifie ton plan..."
                ):

                    response = client.responses.create(
                        model="gpt-5.6-luna",
                        instructions=instructions_plan,
                        input=input_plan
                    )

                st.session_state.feedback_plan = (
                    response.output_text
                )

                st.rerun()

            except Exception as e:

                st.error(
                    "Une erreur s'est produite pendant la vérification du plan."
                )

                st.code(str(e))

    # -----------------------------------------------------
    # LE PLAN A ÉTÉ VÉRIFIÉ
    # -----------------------------------------------------

    else:

        st.subheader("Retour du Coach")

        feedback_plan = st.session_state.feedback_plan

        if feedback_plan.startswith("PLAN VALIDÉ"):

            st.success("✅ Plan validé")

            st.write(
                "Ton plan est suffisamment clair et organisé."
            )

            st.write(
                "**Tu peux commencer la rédaction de l'introduction.**"
            )

            st.info(
                "La rédaction de l'introduction sera ajoutée "
                "à la prochaine étape du Coach."
            )

        else:

            st.write(feedback_plan)

            st.warning(
                "Modifie ton plan avant de poursuivre."
            )

            if st.button("Reprendre mon plan"):
                st.session_state.etape = "plan"
                st.rerun()
