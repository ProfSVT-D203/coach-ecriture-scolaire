import io
import html

import streamlit as st
from openai import OpenAI

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    KeepTogether,
)


# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Coach d'écriture Radio ISTJ",
    page_icon="🎙️",
    layout="centered"
)

MODEL = "gpt-5.6-luna"


# =========================================================
# FONCTIONS GÉNÉRALES
# =========================================================

def initialiser(cle, valeur=""):
    if cle not in st.session_state:
        st.session_state[cle] = valeur


def appel_ia(instructions, contenu):
    client = OpenAI(
        api_key=st.secrets["OPENAI_API_KEY"]
    )

    response = client.responses.create(
        model=MODEL,
        instructions=instructions,
        input=contenu
    )

    return response.output_text


def est_valide(feedback, mot):
    return feedback.strip().startswith(mot)


def assembler_chronique():
    parties = [
        st.session_state.introduction.strip(),
        st.session_state.developpement.strip(),
        st.session_state.conclusion.strip(),
        "",
        "Références :",
        f"Auteur : {st.session_state.ref_auteur.strip()}",
        f"Titre : {st.session_state.ref_titre.strip()}",
        f"Média : {st.session_state.ref_media.strip()}",
        f"Date : {st.session_state.ref_date.strip()}",
    ]

    return "\n\n".join(parties)


def invalider_apres(partie):

    ordre = {
        "comprehension": 1,
        "plan": 2,
        "introduction": 3,
        "developpement": 4,
        "conclusion": 5,
        "references": 6,
    }

    niveau = ordre[partie]

    if niveau <= 1:
        st.session_state.feedback_comprehension = ""

    if niveau <= 2:
        st.session_state.feedback_plan = ""

    if niveau <= 3:
        st.session_state.feedback_introduction = ""

    if niveau <= 4:
        st.session_state.feedback_developpement = ""

    if niveau <= 5:
        st.session_state.feedback_conclusion = ""

    if niveau <= 6:
        st.session_state.feedback_references = ""

    st.session_state.chronique = ""
    st.session_state.feedback_final = ""


# =========================================================
# FONCTIONS PDF
# =========================================================

def texte_pdf(texte):
    """
    Protège le texte de l'élève pour ReportLab sans le réécrire.
    Les retours à la ligne sont conservés.
    """

    texte = str(texte)

    # Quelques caractères susceptibles de poser problème
    # avec les polices PDF standard.
    remplacements = {
        "\u202f": " ",
        "\u00a0": " ",
        "\u2011": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
    }

    for ancien, nouveau in remplacements.items():
        texte = texte.replace(ancien, nouveau)

    texte = html.escape(texte)

    return texte.replace("\n", "<br/>")


def pied_de_page(canvas, doc):
    canvas.saveState()

    largeur, hauteur = A4

    canvas.setStrokeColor(colors.HexColor("#CCCCCC"))
    canvas.setLineWidth(0.5)

    canvas.line(
        2 * cm,
        1.45 * cm,
        largeur - 2 * cm,
        1.45 * cm
    )

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))

    canvas.drawString(
        2 * cm,
        1 * cm,
        "Radio ISTJ - Coach d'écriture"
    )

    canvas.drawRightString(
        largeur - 2 * cm,
        1 * cm,
        f"Page {doc.page}"
    )

    canvas.restoreState()


def generer_pdf():
    """
    Génère le PDF à partir UNIQUEMENT des textes déjà validés
    et stockés dans la session.
    """

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Chronique Radio ISTJ",
        author="Radio ISTJ"
    )

    styles = getSampleStyleSheet()

    style_radio = ParagraphStyle(
        "Radio",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#153A63"),
        spaceAfter=4
    )

    style_sous_titre = ParagraphStyle(
        "SousTitre",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"),
        spaceAfter=18
    )

    style_section = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#153A63"),
        spaceBefore=10,
        spaceAfter=8
    )

    style_texte = ParagraphStyle(
        "TexteChronique",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        spaceAfter=12
    )

    style_reference = ParagraphStyle(
        "References",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#444444"),
        spaceAfter=4
    )

    elements = []

    # -----------------------------------------------------
    # EN-TÊTE
    # -----------------------------------------------------

    elements.append(
        Paragraph(
            "RADIO ISTJ",
            style_radio
        )
    )

    elements.append(
        Paragraph(
            "Chronique élève - version validée",
            style_sous_titre
        )
    )

    infos = (
        f"<b>Niveau :</b> {texte_pdf(st.session_state.niveau)}"
        f"&nbsp;&nbsp;&nbsp;&nbsp;"
        f"<b>Format :</b> {texte_pdf(st.session_state.nombre_voix)}"
    )

    elements.append(
        Paragraph(
            infos,
            style_sous_titre
        )
    )

    elements.append(Spacer(1, 0.2 * cm))

    # -----------------------------------------------------
    # CHRONIQUE
    # -----------------------------------------------------

    elements.append(
        Paragraph(
            "Chronique",
            style_section
        )
    )

    elements.append(
        Paragraph(
            texte_pdf(st.session_state.introduction),
            style_texte
        )
    )

    elements.append(
        Paragraph(
            texte_pdf(st.session_state.developpement),
            style_texte
        )
    )

    elements.append(
        Paragraph(
            texte_pdf(st.session_state.conclusion),
            style_texte
        )
    )

    elements.append(Spacer(1, 0.35 * cm))

    # -----------------------------------------------------
    # RÉFÉRENCES
    # -----------------------------------------------------

    bloc_references = []

    bloc_references.append(
        Paragraph(
            "Références",
            style_section
        )
    )

    bloc_references.append(
        Paragraph(
            f"<b>Auteur :</b> "
            f"{texte_pdf(st.session_state.ref_auteur)}",
            style_reference
        )
    )

    bloc_references.append(
        Paragraph(
            f"<b>Titre :</b> "
            f"{texte_pdf(st.session_state.ref_titre)}",
            style_reference
        )
    )

    bloc_references.append(
        Paragraph(
            f"<b>Média :</b> "
            f"{texte_pdf(st.session_state.ref_media)}",
            style_reference
        )
    )

    bloc_references.append(
        Paragraph(
            f"<b>Date :</b> "
            f"{texte_pdf(st.session_state.ref_date)}",
            style_reference
        )
    )

    elements.append(
        KeepTogether(bloc_references)
    )

    # -----------------------------------------------------
    # CRÉATION
    # -----------------------------------------------------

    document.build(
        elements,
        onFirstPage=pied_de_page,
        onLaterPages=pied_de_page
    )

    pdf = buffer.getvalue()

    buffer.close()

    return pdf


# =========================================================
# VARIABLES DE SESSION
# =========================================================

initialiser("etape", "accueil")

initialiser("niveau", None)
initialiser("nombre_voix", None)
initialiser("source")

initialiser("sujet")
initialiser("idees")
initialiser("vocabulaire")
initialiser("feedback_comprehension")

initialiser("plan_introduction")
initialiser("plan_developpement")
initialiser("plan_conclusion")
initialiser("plan_repartition")
initialiser("feedback_plan")

initialiser("introduction")
initialiser("feedback_introduction")

initialiser("developpement")
initialiser("feedback_developpement")

initialiser("conclusion")
initialiser("feedback_conclusion")

initialiser("ref_auteur")
initialiser("ref_titre")
initialiser("ref_media")
initialiser("ref_date")
initialiser("feedback_references")

initialiser("chronique")
initialiser("feedback_final")


# =========================================================
# PROMPT COMMUN POUR LA RÉDACTION
# =========================================================

REGLES_REDACTION = """
Tu es le Coach d'écriture pédagogique de Radio ISTJ.

Tu accompagnes un élève de collège qui écrit lui-même une chronique radio
à partir d'une source fournie.

RÈGLE ABSOLUE :
L'élève est l'auteur.

Tu ne dois JAMAIS :
- écrire une phrase de chronique à sa place ;
- proposer une reformulation prête à copier ;
- proposer une introduction modèle ;
- proposer une conclusion modèle ;
- donner un début ou une fin de phrase ;
- rédiger une transition ;
- rédiger une réplique pour une voix ;
- fournir une version améliorée du passage.

Tu peux seulement :
- analyser ce que l'élève a écrit ;
- signaler UNE difficulté réellement importante ;
- poser UNE question ciblée ;
- donner quelques mots-clés ou une indication de structure si nécessaire.

FIDÉLITÉ :
Travaille uniquement avec la source fournie.
N'ajoute aucune connaissance extérieure.

SÉLECTIONNER N'EST PAS DÉFORMER.

Une chronique radio n'est pas un résumé exhaustif.
L'élève peut sélectionner seulement certaines informations exactes.

Une information exacte ne devient pas insuffisante parce que la source
permettrait d'en dire davantage.

N'exige jamais automatiquement :
- toutes les causes ;
- tous les nombres ;
- toutes les dates ;
- tous les exemples ;
- toutes les étapes ;
- toutes les conséquences ;
- tous les détails.

Distingue :
1. information fausse ou déformée ;
2. information sélectionnée mais exacte ;
3. information réellement trop vague pour remplir son rôle.

ANTI-PLAGIAT :
Les noms propres, dates, nombres, lieux, termes scientifiques,
organismes et données factuelles peuvent rester identiques.

En revanche, signale un risque de plagiat si l'élève reprend :
- une phrase entière ou presque entière ;
- la même construction avec presque les mêmes mots ;
- plusieurs expressions caractéristiques de la source dans le même ordre.

NIVEAU 6e-5e :
- accepte des phrases courtes ;
- accepte un vocabulaire simple ;
- accepte une organisation simple ;
- accepte 2 ou 3 idées essentielles ;
- ne demande pas davantage de détails si l'auditeur comprend déjà
  suffisamment l'idée.

NIVEAU 4e-3e :
attends davantage :
- de précision ;
- de vocabulaire adapté ;
- d'explications ;
- de liens entre les idées ;
- de progression logique.

Mais même en 4e-3e, n'exige jamais l'exhaustivité.

SI UNE CORRECTION EST NÉCESSAIRE :
- indique brièvement ce qui fonctionne déjà ;
- choisis UNE SEULE difficulté prioritaire ;
- explique le problème sans écrire la solution ;
- pose UNE question ciblée ;
- laisse l'élève corriger lui-même.

Ne donne pas directement l'information correcte si l'élève peut
la retrouver dans sa source.

Ne cherche pas la meilleure chronique possible.
Cherche seulement à savoir si le passage atteint le seuil nécessaire
pour une chronique de collège destinée à être entendue à la radio.
"""


# =========================================================
# TITRE
# =========================================================

st.title("🎙️ Coach d'écriture Radio ISTJ")


# =========================================================
# ÉTAPE 0 - ACCUEIL
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

        if not source.strip():

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
# ÉTAPE 1 - COMPRÉHENSION
# =========================================================

elif st.session_state.etape == "comprehension":

    st.subheader("Étape 1 - Comprendre la source")

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
        height=160
    )

    vocabulaire = st.text_area(
        "Y a-t-il un mot ou un passage que tu ne comprends pas ? "
        "Si tout est clair, écris simplement : Aucun.",
        value=st.session_state.vocabulaire
    )

    if st.button("Continuer"):

        if not sujet.strip():

            st.warning(
                "Indique d'abord le sujet principal."
            )

        elif not idees.strip():

            st.warning(
                "Indique les idées importantes que tu as retenues."
            )

        elif not vocabulaire.strip():

            st.warning(
                "Indique les difficultés rencontrées ou écris « Aucun »."
            )

        else:

            st.session_state.sujet = sujet
            st.session_state.idees = idees
            st.session_state.vocabulaire = vocabulaire

            invalider_apres("comprehension")

            st.session_state.etape = "analyse_comprehension"

            st.rerun()


# =========================================================
# ÉTAPE 1B - CONTRÔLE COMPRÉHENSION
# =========================================================

elif st.session_state.etape == "analyse_comprehension":

    st.subheader("Compréhension enregistrée")

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

    if not st.session_state.feedback_comprehension:

        if st.button("🤖 Vérifier ma compréhension"):

            instructions = """
Tu vérifies uniquement l'étape de compréhension d'une source
par un élève de collège.

Tu dois vérifier :
- le sujet principal ;
- chacune des 2 ou 3 idées importantes ;
- les éventuelles difficultés de vocabulaire.

SÉLECTIONNER N'EST PAS DÉFORMER.

Une idée exacte ne doit pas être critiquée simplement parce que
la source permettrait d'en dire davantage.

Si l'élève signale un mot incompris, explique ce mot avec un vocabulaire
adapté au niveau, sans rédiger la chronique.

Si une erreur importante subsiste :
- ne donne pas la bonne réponse ;
- indique l'idée concernée ;
- pose UNE question qui permet à l'élève de retrouver lui-même
  l'information dans la source.

Si toutes les réponses montrent une compréhension suffisante,
réponds exactement :

COMPRÉHENSION VALIDÉE
Tu as bien compris les idées essentielles de la source.
Tu peux passer à la construction du plan.

Sinon commence exactement par :

À REVOIR

Puis donne une seule aide prioritaire.
"""

            contenu = f"""
NIVEAU :
{st.session_state.niveau}

SOURCE :
{st.session_state.source}

SUJET PRINCIPAL ÉCRIT PAR L'ÉLÈVE :
{st.session_state.sujet}

IDÉES IMPORTANTES :
{st.session_state.idees}

VOCABULAIRE / DIFFICULTÉS :
{st.session_state.vocabulaire}
"""

            try:

                with st.spinner(
                    "Le Coach vérifie ta compréhension..."
                ):

                    st.session_state.feedback_comprehension = appel_ia(
                        instructions,
                        contenu
                    )

                st.rerun()

            except Exception as e:

                st.error("Erreur pendant la vérification.")
                st.code(str(e))

    else:

        if est_valide(
            st.session_state.feedback_comprehension,
            "COMPRÉHENSION VALIDÉE"
        ):

            st.success("✅ Compréhension validée")

            st.write(
                "Tu as bien compris les idées essentielles de la source."
            )

            if st.button("Construire mon plan"):

                st.session_state.etape = "plan"
                st.rerun()

        else:

            st.subheader("Retour du Coach")
            st.write(st.session_state.feedback_comprehension)

            st.warning(
                "Corrige tes réponses avant de poursuivre."
            )

            if st.button("Reprendre mes réponses"):

                st.session_state.etape = "comprehension"
                st.rerun()


# =========================================================
# ÉTAPE 2 - PLAN
# =========================================================

elif st.session_state.etape == "plan":

    st.subheader("Étape 2 - Construire le plan")

    st.write(
        "Indique ce que tu veux faire dans chaque partie. "
        "Tu n'écris pas encore les phrases de ta chronique."
    )

    st.divider()

    plan_introduction = st.text_area(
        "Introduction - Que veux-tu présenter au début ?",
        value=st.session_state.plan_introduction
    )

    plan_developpement = st.text_area(
        "Développement - Quelles idées veux-tu expliquer, et dans quel ordre ?",
        value=st.session_state.plan_developpement,
        height=170
    )

    plan_conclusion = st.text_area(
        "Conclusion - Sur quelle idée veux-tu terminer ?",
        value=st.session_state.plan_conclusion
    )

    if st.session_state.nombre_voix != "1 voix":

        plan_repartition = st.text_area(
            f"Répartition des {st.session_state.nombre_voix} - "
            "Qui intervient dans les différentes parties ?",
            value=st.session_state.plan_repartition,
            height=140
        )

    else:

        plan_repartition = ""

    if st.button("Enregistrer mon plan"):

        manque = (
            not plan_introduction.strip()
            or not plan_developpement.strip()
            or not plan_conclusion.strip()
        )

        if manque:

            st.warning(
                "Complète l'introduction, le développement et la conclusion."
            )

        elif (
            st.session_state.nombre_voix != "1 voix"
            and not plan_repartition.strip()
        ):

            st.warning(
                "Indique comment les voix seront réparties."
            )

        else:

            st.session_state.plan_introduction = plan_introduction
            st.session_state.plan_developpement = plan_developpement
            st.session_state.plan_conclusion = plan_conclusion
            st.session_state.plan_repartition = plan_repartition

            invalider_apres("plan")

            st.session_state.etape = "plan_enregistre"

            st.rerun()


# =========================================================
# ÉTAPE 2B - CONTRÔLE PLAN
# =========================================================

elif st.session_state.etape == "plan_enregistre":

    st.subheader("Plan enregistré")

    st.write("### Introduction")
    st.write(st.session_state.plan_introduction)

    st.write("### Développement")
    st.write(st.session_state.plan_developpement)

    st.write("### Conclusion")
    st.write(st.session_state.plan_conclusion)

    if st.session_state.nombre_voix != "1 voix":
        st.write("### Répartition des voix")
        st.write(st.session_state.plan_repartition)

    st.divider()

    if st.button("Modifier mon plan"):

        st.session_state.etape = "plan"
        st.rerun()

    st.divider()

    if not st.session_state.feedback_plan:

        if st.button("🤖 Faire vérifier mon plan par le Coach"):

            instructions = """
Tu vérifies uniquement le plan d'une chronique radio.

Le plan peut être très simple et rédigé sous forme de notes.

Il doit permettre de préparer :
- une introduction ;
- un développement ;
- une conclusion.

Pour plusieurs voix, vérifie également que la répartition
des interventions est exploitable.

N'exige pas une alternance parfaite entre les voix.

SÉLECTIONNER N'EST PAS DÉFORMER.

Pour 6e-5e, un plan simple avec 2 ou 3 idées essentielles
suffisamment identifiées peut être accepté.

N'exige pas tous les nombres, toutes les causes ou tous les détails.

Pour 4e-3e, attends davantage de précision et d'organisation,
mais jamais l'exhaustivité.

Tu ne rédiges aucune phrase de chronique.

Si le plan est suffisant, réponds exactement :

PLAN VALIDÉ
Ton plan est suffisamment clair et organisé.
Tu peux commencer la rédaction de l'introduction.

Sinon commence exactement par :

À REVOIR

Puis signale UNE seule difficulté prioritaire
et pose UNE question ciblée sans réécrire le plan.
"""

            contenu = f"""
NIVEAU :
{st.session_state.niveau}

FORMAT :
{st.session_state.nombre_voix}

SOURCE :
{st.session_state.source}

SUJET COMPRIS :
{st.session_state.sujet}

IDÉES IMPORTANTES :
{st.session_state.idees}

INTRODUCTION PRÉVUE :
{st.session_state.plan_introduction}

DÉVELOPPEMENT PRÉVU :
{st.session_state.plan_developpement}

CONCLUSION PRÉVUE :
{st.session_state.plan_conclusion}

RÉPARTITION DES VOIX :
{st.session_state.plan_repartition}
"""

            try:

                with st.spinner("Le Coach vérifie ton plan..."):

                    st.session_state.feedback_plan = appel_ia(
                        instructions,
                        contenu
                    )

                st.rerun()

            except Exception as e:

                st.error("Erreur pendant la vérification du plan.")
                st.code(str(e))

    else:

        if est_valide(
            st.session_state.feedback_plan,
            "PLAN VALIDÉ"
        ):

            st.success("✅ Plan validé")

            st.write(
                "Ton plan est suffisamment clair et organisé."
            )

            if st.button("Rédiger mon introduction"):

                st.session_state.etape = "introduction"
                st.rerun()

        else:

            st.subheader("Retour du Coach")
            st.write(st.session_state.feedback_plan)

            if st.button("Reprendre mon plan"):

                st.session_state.etape = "plan"
                st.rerun()


# =========================================================
# ÉTAPE 3 - INTRODUCTION
# =========================================================

elif st.session_state.etape == "introduction":

    st.subheader("Étape 3 - Rédiger l'introduction")

    st.write(
        "Écris maintenant toi-même ton introduction."
    )

    st.info(
        "Elle doit permettre à l'auditeur d'identifier le sujet "
        "et de comprendre pourquoi il mérite une chronique."
    )

    if st.session_state.nombre_voix != "1 voix":

        st.write(
            f"Pour une chronique à {st.session_state.nombre_voix}, "
            "indique clairement les voix, par exemple « Voix 1 : »."
        )

    st.write("### Ton plan")
    st.write(st.session_state.plan_introduction)

    introduction = st.text_area(
        "Ton introduction :",
        value=st.session_state.introduction,
        height=170
    )

    if st.button("Enregistrer mon introduction"):

        if not introduction.strip():

            st.warning("Écris d'abord ton introduction.")

        else:

            st.session_state.introduction = introduction

            invalider_apres("introduction")

            st.session_state.etape = "controle_introduction"

            st.rerun()


# =========================================================
# ÉTAPE 3B - CONTRÔLE INTRODUCTION
# =========================================================

elif st.session_state.etape == "controle_introduction":

    st.subheader("Ton introduction")

    st.write(st.session_state.introduction)

    if st.button("Modifier mon introduction"):

        st.session_state.etape = "introduction"
        st.rerun()

    st.divider()

    if not st.session_state.feedback_introduction:

        if st.button("🤖 Vérifier mon introduction"):

            instructions = REGLES_REDACTION + """

TU CONTRÔLES UNIQUEMENT L'INTRODUCTION.

RÔLE DE L'INTRODUCTION :

L'introduction doit seulement permettre :
1. d'identifier suffisamment le sujet de la chronique ;
2. de comprendre pourquoi ce sujet peut présenter un intérêt
   pour l'auditeur.

Elle n'a PAS pour rôle d'expliquer déjà le développement.

RÈGLE TRÈS IMPORTANTE POUR 6e-5e :

Une ou deux phrases simples peuvent suffire.

Si le sujet est identifiable et qu'au moins un élément permet
de comprendre son intérêt, l'introduction DOIT être validée.

NE BLOQUE JAMAIS une introduction correcte de niveau 6e-5e
simplement parce qu'elle n'explique pas encore :
- comment fonctionne une technique ;
- son mécanisme ;
- une cause ;
- une conséquence ;
- les résultats ;
- une date ;
- un nombre ;
- une statistique ;
- un lieu plus précis ;
- un exemple ;
- un détail scientifique ou technique.

Ces informations peuvent naturellement être expliquées
dans le développement.

CAS IMPORTANT :

Une introduction de niveau 6e-5e qui annonce clairement
« une nouvelle technique testée pour lutter contre le cancer
du pancréas » identifie suffisamment le sujet et son intérêt.

Elle ne doit PAS être refusée au motif qu'elle n'explique pas encore
comment cette technique agit sur la tumeur.

Ne transforme jamais une possibilité d'enrichissement
en condition obligatoire de validation.

UNE INTRODUCTION DOIT ÊTRE REFUSÉE seulement si, par exemple :
- le sujet n'est pas identifiable ;
- elle contient une erreur importante ;
- elle déforme la source ;
- elle est tellement générale qu'elle pourrait convenir
  à presque n'importe quel sujet ;
- elle reprend de manière trop proche une phrase de la source ;
- elle est réellement incompréhensible à la première écoute.

Pour 4e-3e :
tu peux attendre davantage de précision et de contextualisation,
mais sans demander que l'introduction contienne déjà
les explications du développement.

Vérifie aussi :
- fidélité à la source ;
- formulation personnelle ;
- compréhension à la première écoute ;
- respect du plan.

Pour plusieurs voix :
les répliques doivent être clairement identifiables.

AVANT DE REFUSER L'INTRODUCTION, pose-toi obligatoirement
cette question :

« L'information que je souhaite demander est-elle indispensable
pour identifier le sujet et comprendre son intérêt,
ou pourrait-elle normalement être expliquée dans le développement ? »

Si elle peut normalement être expliquée dans le développement,
NE LA DEMANDE PAS et valide l'introduction si le reste est correct.

Si l'introduction est suffisante, réponds exactement :

INTRODUCTION VALIDÉE
L'introduction remplit son rôle.
Tu peux passer au développement.

Sinon commence exactement par :

À REVOIR

Puis applique les règles d'aide définies plus haut.
"""

            contenu = f"""
NIVEAU :
{st.session_state.niveau}

FORMAT :
{st.session_state.nombre_voix}

SOURCE :
{st.session_state.source}

PLAN DE L'INTRODUCTION :
{st.session_state.plan_introduction}

INTRODUCTION ÉCRITE PAR L'ÉLÈVE :
{st.session_state.introduction}
"""

            try:

                with st.spinner(
                    "Le Coach vérifie ton introduction..."
                ):

                    st.session_state.feedback_introduction = appel_ia(
                        instructions,
                        contenu
                    )

                st.rerun()

            except Exception as e:

                st.error("Erreur pendant la vérification.")
                st.code(str(e))

    else:

        if est_valide(
            st.session_state.feedback_introduction,
            "INTRODUCTION VALIDÉE"
        ):

            st.success("✅ Introduction validée")

            if st.button("Passer au développement"):

                st.session_state.etape = "developpement"
                st.rerun()

        else:

            st.subheader("Retour du Coach")
            st.write(st.session_state.feedback_introduction)

            if st.button("Corriger mon introduction"):

                st.session_state.etape = "introduction"
                st.rerun()


# =========================================================
# ÉTAPE 4 - DÉVELOPPEMENT
# =========================================================

elif st.session_state.etape == "developpement":

    st.subheader("Étape 4 - Rédiger le développement")

    st.write(
        "Écris maintenant le développement avec tes propres phrases."
    )

    st.write("### Ton plan")
    st.write(st.session_state.plan_developpement)

    if st.session_state.nombre_voix != "1 voix":

        st.write("### Répartition prévue")
        st.write(st.session_state.plan_repartition)

        st.info(
            "Indique clairement la voix qui prononce chaque réplique."
        )

    developpement = st.text_area(
        "Ton développement :",
        value=st.session_state.developpement,
        height=320
    )

    if st.button("Enregistrer mon développement"):

        if not developpement.strip():

            st.warning("Écris d'abord ton développement.")

        else:

            st.session_state.developpement = developpement

            invalider_apres("developpement")

            st.session_state.etape = "controle_developpement"

            st.rerun()


# =========================================================
# ÉTAPE 4B - CONTRÔLE DÉVELOPPEMENT
# =========================================================

elif st.session_state.etape == "controle_developpement":

    st.subheader("Ton développement")

    st.write(st.session_state.developpement)

    if st.button("Modifier mon développement"):

        st.session_state.etape = "developpement"
        st.rerun()

    st.divider()

    if not st.session_state.feedback_developpement:

        if st.button("🤖 Vérifier mon développement"):

            instructions = REGLES_REDACTION + """

TU CONTRÔLES UNIQUEMENT LE DÉVELOPPEMENT.

=========================================================
1. RÔLE DU DÉVELOPPEMENT
=========================================================

Compare le développement :
- à la source ;
- au plan choisi par l'élève.

Vérifie que les idées prévues dans le plan ont réellement été traitées.

Le point de comparaison principal est le PLAN de l'élève,
PAS l'ensemble des informations disponibles dans la source.

Le développement n'a pas à reprendre tout l'article.

SÉLECTIONNER N'EST PAS DÉFORMER.

Une information exacte ne devient pas insuffisante simplement parce
que la source permettrait de donner davantage de détails.


=========================================================
2. FIDÉLITÉ
=========================================================

Une correction est nécessaire si une information :
- est fausse ;
- inverse le sens de la source ;
- déforme réellement une idée ;
- présente comme certain quelque chose qui ne l'est pas ;
- ajoute un fait absent ;
- crée une relation de cause à effet absente.

NE CORRIGE PAS simplement parce que :
- l'information pourrait être plus détaillée ;
- un terme plus précis existe ;
- un nombre est absent ;
- plusieurs exemples existent ;
- une procédure plus complète est disponible.


=========================================================
3. NIVEAU 6e-5e
=========================================================

Accepte :
- phrases courtes ;
- vocabulaire simple ;
- organisation simple ;
- quelques informations essentielles ;
- 2 ou 3 idées correctement expliquées.

N'exige pas systématiquement :
- plusieurs causes ;
- nombres ;
- dates ;
- durées ;
- tous les exemples ;
- toutes les étapes ;
- détails scientifiques ou techniques.


=========================================================
4. NIVEAU 4e-3e
=========================================================

Attends davantage :
- de précision ;
- d'explication ;
- de vocabulaire adapté ;
- de liens entre les idées ;
- de progression logique.

Une idée prévue dans le plan peut nécessiter une explication
si l'élève affirme seulement un résultat sans permettre
de comprendre suffisamment le phénomène.

Mais même en 4e-3e :

N'EXIGE JAMAIS L'EXHAUSTIVITÉ.


=========================================================
5. INTERPRÉTATION DU PLAN
=========================================================

Le plan est un guide de rédaction.

Mais tu ne dois PAS interpréter chaque verbe du plan
comme une obligation de fournir tous les détails techniques possibles.

LE MOT « COMMENT » NE SIGNIFIE PAS AUTOMATIQUEMENT
« DÉCRIRE TOUTE LA PROCÉDURE TECHNIQUE ».

Lorsque le plan prévoit :
- expliquer comment une technique agit ;
- expliquer comment un traitement est utilisé ;
- expliquer comment un produit est placé ;
- expliquer comment une action est réalisée ;

cherche d'abord le PRINCIPE nécessaire à la compréhension.

Une explication conceptuelle simple peut suffire.

N'exige PAS automatiquement :
- les instruments ;
- les appareils ;
- le matériel ;
- tous les gestes ;
- toutes les étapes opératoires ;
- tous les détails de positionnement ;
- tous les nombres de la procédure.

Ces informations deviennent obligatoires seulement si :

1. le plan les mentionne explicitement ;

OU

2. leur absence empêche réellement de comprendre le principe.

EXEMPLE DE RÉFÉRENCE :

PLAN :
« Expliquer comment le radium 224 est placé dans la tumeur. »

DÉVELOPPEMENT :
« Des bâtonnets avec du radium 224 sont placés directement
dans la tumeur. »

Pour un élève de 4e-3e,
cette information peut suffire à faire comprendre
le principe de l'implantation.

N'exige pas automatiquement :
- l'endoscope ;
- l'aiguille ;
- le nombre exact de bâtonnets ;
- leur positionnement précis ;
- la procédure opératoire complète.

« Expliquer comment » peut être satisfait
par une explication du principe.


=========================================================
6. RÈGLE D'ARRÊT
=========================================================

Tu dois savoir ARRÊTER la correction.

Dès que les idées prévues dans le plan :
- sont présentes ;
- sont fidèles ;
- sont suffisamment expliquées pour le niveau ;

le développement DOIT être validé.

Ne demande pas ensuite :
- instrument ;
- chiffre ;
- date ;
- durée ;
- étape technique ;
- détail de procédure ;
- exemple supplémentaire ;
- précision scientifique supplémentaire

simplement parce que cette information existe dans la source.


=========================================================
7. TEST DE DÉCISION
=========================================================

Avant chaque « À REVOIR », demande-toi :

1. L'idée demandée par le plan est-elle présente ?
2. Son principe essentiel est-il compréhensible ?
3. L'information supplémentaire est-elle indispensable ?

Si :

1. OUI
2. OUI
3. NON

alors tu DOIS valider cette idée.

Ne confonds jamais :

« le texte pourrait être plus détaillé »

avec

« le texte est insuffisant ».

Si tu constates toi-même que toutes les idées du plan
sont présentes, fidèles et suffisamment expliquées,
tu DOIS valider.


=========================================================
8. QUALITÉ RADIO
=========================================================

Le développement doit être compréhensible à la première écoute.

Une formulation simple, scolaire ou imparfaite
peut être acceptée si elle reste claire.

Ne cherche pas une chronique parfaite.


=========================================================
9. PLUSIEURS VOIX
=========================================================

Pour 2 ou 3 voix :
- les répliques doivent être identifiables ;
- la répartition doit rester cohérente ;
- l'ensemble doit être compréhensible.

N'exige pas :
- une alternance parfaite ;
- le même nombre de phrases ;
- la même durée de parole.


=========================================================
10. PLAGIAT
=========================================================

Les noms, dates, nombres, lieux et termes scientifiques nécessaires
peuvent être identiques à ceux de la source.

Signale seulement :
- phrase entière ou presque entière copiée ;
- même construction avec presque les mêmes mots ;
- plusieurs expressions caractéristiques dans le même ordre.


=========================================================
11. VALIDATION
=========================================================

Si les idées prévues dans le plan sont :
- présentes ;
- fidèles ;
- suffisamment expliquées ;
- compréhensibles à l'oral ;
- suffisamment reformulées ;

réponds EXACTEMENT :

DÉVELOPPEMENT VALIDÉ
Le développement remplit son rôle.
Tu peux passer à la conclusion.


=========================================================
12. CORRECTION
=========================================================

Si une correction est réellement nécessaire,
commence EXACTEMENT par :

À REVOIR

Puis :
- dis brièvement ce qui fonctionne ;
- choisis UNE seule difficulté ;
- explique pourquoi elle bloque réellement la compréhension ;
- ne rédige pas la correction ;
- pose UNE seule question ciblée ;
- laisse l'élève corriger lui-même.

Après correction, applique à nouveau la règle d'arrêt.

Ne cherche pas immédiatement un nouveau détail.

PRINCIPE FINAL :

SÉLECTIONNER N'EST PAS DÉFORMER.

SUFFISAMMENT EXPLIQUÉ N'EST PAS INSUFFISAMMENT DÉTAILLÉ.

EXPLIQUER UN PRINCIPE N'IMPOSE PAS DE DÉCRIRE
TOUTE LA PROCÉDURE TECHNIQUE.
"""

            contenu = f"""
NIVEAU :
{st.session_state.niveau}

FORMAT :
{st.session_state.nombre_voix}

SOURCE :
{st.session_state.source}

PLAN DU DÉVELOPPEMENT :
{st.session_state.plan_developpement}

RÉPARTITION PRÉVUE :
{st.session_state.plan_repartition}

DÉVELOPPEMENT ÉCRIT PAR L'ÉLÈVE :
{st.session_state.developpement}
"""

            try:

                with st.spinner(
                    "Le Coach vérifie ton développement..."
                ):

                    st.session_state.feedback_developpement = appel_ia(
                        instructions,
                        contenu
                    )

                st.rerun()

            except Exception as e:

                st.error("Erreur pendant la vérification.")
                st.code(str(e))

    else:

        if est_valide(
            st.session_state.feedback_developpement,
            "DÉVELOPPEMENT VALIDÉ"
        ):

            st.success("✅ Développement validé")

            if st.button("Passer à la conclusion"):

                st.session_state.etape = "conclusion"
                st.rerun()

        else:

            st.subheader("Retour du Coach")
            st.write(st.session_state.feedback_developpement)

            if st.button("Corriger mon développement"):

                st.session_state.etape = "developpement"
                st.rerun()


# =========================================================
# ÉTAPE 5 - CONCLUSION
# =========================================================

elif st.session_state.etape == "conclusion":

    st.subheader("Étape 5 - Rédiger la conclusion")

    st.write(
        "Écris maintenant toi-même la conclusion de ta chronique."
    )

    st.write("### Ton plan")
    st.write(st.session_state.plan_conclusion)

    if st.session_state.nombre_voix != "1 voix":

        st.info(
            "Si plusieurs voix interviennent dans la conclusion, "
            "indique-les clairement."
        )

    conclusion = st.text_area(
        "Ta conclusion :",
        value=st.session_state.conclusion,
        height=170
    )

    if st.button("Enregistrer ma conclusion"):

        if not conclusion.strip():

            st.warning("Écris d'abord ta conclusion.")

        else:

            st.session_state.conclusion = conclusion

            invalider_apres("conclusion")

            st.session_state.etape = "controle_conclusion"

            st.rerun()


# =========================================================
# ÉTAPE 5B - CONTRÔLE CONCLUSION
# =========================================================

elif st.session_state.etape == "controle_conclusion":

    st.subheader("Ta conclusion")

    st.write(st.session_state.conclusion)

    if st.button("Modifier ma conclusion"):

        st.session_state.etape = "conclusion"
        st.rerun()

    st.divider()

    if not st.session_state.feedback_conclusion:

        if st.button("🤖 Vérifier ma conclusion"):

            instructions = REGLES_REDACTION + """

TU CONTRÔLES UNIQUEMENT LA CONCLUSION.

Une conclusion doit apporter une véritable idée de fin.

Elle peut notamment :
- rappeler ce qu'il faut retenir ;
- présenter un enjeu ;
- présenter une conséquence ;
- évoquer une perspective ;
- montrer un espoir ou une incertitude présente dans la source ;
- contenir une courte appréciation personnelle clairement identifiable.

Pour 6e-5e :
une seule phrase simple peut suffire.

Ne demande pas une information supplémentaire simplement
pour rendre la conclusion plus riche.

En revanche, ne valide pas une conclusion tellement vague,
répétitive ou circulaire qu'elle n'apporte pas réellement de fin.

Vérifie :
- fidélité lorsqu'elle contient des faits ;
- absence de fait inventé ;
- formulation personnelle ;
- clarté à l'oral ;
- respect du plan.

Si la conclusion est suffisante, réponds exactement :

CONCLUSION VALIDÉE
La conclusion apporte une véritable idée de fin.
Tu peux passer aux références.

Sinon commence exactement par :

À REVOIR

Puis applique les règles d'aide.
"""

            contenu = f"""
NIVEAU :
{st.session_state.niveau}

SOURCE :
{st.session_state.source}

PLAN DE LA CONCLUSION :
{st.session_state.plan_conclusion}

CONCLUSION ÉCRITE PAR L'ÉLÈVE :
{st.session_state.conclusion}
"""

            try:

                with st.spinner(
                    "Le Coach vérifie ta conclusion..."
                ):

                    st.session_state.feedback_conclusion = appel_ia(
                        instructions,
                        contenu
                    )

                st.rerun()

            except Exception as e:

                st.error("Erreur pendant la vérification.")
                st.code(str(e))

    else:

        if est_valide(
            st.session_state.feedback_conclusion,
            "CONCLUSION VALIDÉE"
        ):

            st.success("✅ Conclusion validée")

            if st.button("Indiquer mes références"):

                st.session_state.etape = "references"
                st.rerun()

        else:

            st.subheader("Retour du Coach")
            st.write(st.session_state.feedback_conclusion)

            if st.button("Corriger ma conclusion"):

                st.session_state.etape = "conclusion"
                st.rerun()


# =========================================================
# ÉTAPE 6 - RÉFÉRENCES
# =========================================================

elif st.session_state.etape == "references":

    st.subheader("Étape 6 - Retrouver les références")

    st.write(
        "Retrouve toi-même ces informations dans ta source."
    )

    st.info(
        "Si une information n'est pas indiquée dans la source, "
        "écris « Non indiqué »."
    )

    ref_auteur = st.text_input(
        "Auteur :",
        value=st.session_state.ref_auteur
    )

    ref_titre = st.text_input(
        "Titre :",
        value=st.session_state.ref_titre
    )

    ref_media = st.text_input(
        "Média :",
        value=st.session_state.ref_media
    )

    ref_date = st.text_input(
        "Date :",
        value=st.session_state.ref_date
    )

    if st.button("Enregistrer mes références"):

        if not all([
            ref_auteur.strip(),
            ref_titre.strip(),
            ref_media.strip(),
            ref_date.strip()
        ]):

            st.warning(
                "Complète les quatre champs. "
                "Écris « Non indiqué » lorsque l'information est absente."
            )

        else:

            st.session_state.ref_auteur = ref_auteur
            st.session_state.ref_titre = ref_titre
            st.session_state.ref_media = ref_media
            st.session_state.ref_date = ref_date

            invalider_apres("references")

            st.session_state.etape = "controle_references"

            st.rerun()


# =========================================================
# ÉTAPE 6B - CONTRÔLE RÉFÉRENCES
# =========================================================

elif st.session_state.etape == "controle_references":

    st.subheader("Tes références")

    st.write(f"**Auteur :** {st.session_state.ref_auteur}")
    st.write(f"**Titre :** {st.session_state.ref_titre}")
    st.write(f"**Média :** {st.session_state.ref_media}")
    st.write(f"**Date :** {st.session_state.ref_date}")

    if st.button("Modifier mes références"):

        st.session_state.etape = "references"
        st.rerun()

    st.divider()

    if not st.session_state.feedback_references:

        if st.button("🤖 Vérifier mes références"):

            instructions = """
Tu vérifies uniquement les références identifiées par un élève.

Compare-les avec la SOURCE.

L'élève doit avoir lui-même fourni :
- l'auteur, s'il est indiqué ;
- le titre ;
- le média ;
- la date, si elle est disponible.

Si une information n'existe pas dans la source,
« Non indiqué » peut être accepté.

Tu ne fabriques jamais toi-même une référence
pour remplacer le travail de l'élève.

Si les références correspondent suffisamment à la source,
réponds exactement :

RÉFÉRENCES VALIDÉES
Les références correspondent à la source.

Sinon commence exactement par :

À REVOIR

Indique UNE seule information bibliographique à vérifier.
Ne donne pas directement la bonne réponse si l'élève peut
la retrouver lui-même dans la source.
"""

            contenu = f"""
SOURCE :
{st.session_state.source}

RÉFÉRENCES DONNÉES PAR L'ÉLÈVE :

Auteur :
{st.session_state.ref_auteur}

Titre :
{st.session_state.ref_titre}

Média :
{st.session_state.ref_media}

Date :
{st.session_state.ref_date}
"""

            try:

                with st.spinner(
                    "Le Coach vérifie les références..."
                ):

                    st.session_state.feedback_references = appel_ia(
                        instructions,
                        contenu
                    )

                st.rerun()

            except Exception as e:

                st.error("Erreur pendant la vérification.")
                st.code(str(e))

    else:

        if est_valide(
            st.session_state.feedback_references,
            "RÉFÉRENCES VALIDÉES"
        ):

            st.success("✅ Références validées")

            if st.button("Assembler ma chronique"):

                st.session_state.chronique = assembler_chronique()
                st.session_state.feedback_final = ""
                st.session_state.etape = "chronique_assemblee"

                st.rerun()

        else:

            st.subheader("Retour du Coach")
            st.write(st.session_state.feedback_references)

            if st.button("Corriger mes références"):

                st.session_state.etape = "references"
                st.rerun()


# =========================================================
# ÉTAPE 7 - ASSEMBLAGE
# =========================================================

elif st.session_state.etape == "chronique_assemblee":

    st.subheader("Étape 7 - Chronique assemblée")

    st.success(
        "La chronique a été assemblée uniquement avec les textes "
        "que tu as écrits."
    )

    st.text_area(
        "Ta chronique complète :",
        value=st.session_state.chronique,
        height=450,
        disabled=True
    )

    st.info(
        "Il reste un dernier contrôle indépendant avant validation."
    )

    if st.button("🔎 Lancer le contrôle final"):

        st.session_state.etape = "controle_final"
        st.rerun()


# =========================================================
# ÉTAPE 8 - CONTRÔLE FINAL INDÉPENDANT
# =========================================================

elif st.session_state.etape == "controle_final":

    st.subheader("Étape 8 - Contrôle final")

    if not st.session_state.feedback_final:

        instructions = """
Tu es chargé du CONTRÔLE FINAL INDÉPENDANT
d'une chronique Radio ISTJ écrite par un élève de collège.

Tu disposes :
- du niveau ;
- de la source originale ;
- de la chronique complète de l'élève.

Tu ne réécris rien.
Tu ne cherches pas à améliorer le texte.
Tu détectes uniquement les problèmes qui rendent réellement
une correction obligatoire avant validation.

=========================================================
1. FIDÉLITÉ
=========================================================

Toute information factuelle de la chronique doit être justifiable
par la source.

Signale :
- information contraire à la source ;
- déformation réelle ;
- attribution incorrecte ;
- relation de cause à effet absente ;
- affirmation plus forte que ce que permet la source.

RÈGLE PRIORITAIRE :
SÉLECTIONNER N'EST PAS DÉFORMER.

Une chronique n'est pas un résumé exhaustif.

L'omission d'informations présentes dans la source n'est PAS
une erreur de fidélité.

Si l'élève sélectionne certaines causes, certains exemples,
certaines conséquences ou certains détails exacts,
cette sélection est fidèle tant qu'il ne prétend pas
qu'il s'agit de la liste complète.

N'infère jamais une exclusivité qui n'est pas écrite.

« à cause de X » ne signifie pas
« uniquement à cause de X ».

Distingue toujours :

INFORMATION NON FIDÈLE :
ce que dit l'élève ne correspond pas à la source.

INFORMATION SÉLECTIONNÉE :
l'élève utilise seulement certaines informations exactes.
Ce n'est PAS un problème.

QUALITÉ RADIO INSUFFISANTE :
l'information est correcte mais réellement trop vague
pour permettre à l'auditeur de comprendre.


=========================================================
2. EXACTITUDE
=========================================================

Vérifie particulièrement :
- nombres ;
- statistiques ;
- dates ;
- durées ;
- quantités ;
- lieux ;
- noms propres ;
- noms d'espèces ;
- organismes ;
- unités.

Une donnée présente doit être exacte.

Son absence n'est pas une erreur si l'élève n'en avait pas besoin.


=========================================================
3. INFORMATION INVENTÉE
=========================================================

Signale un fait présenté comme réel s'il :
- n'apparaît pas dans la source ;
- ne peut pas raisonnablement en être déduit ;
- ajoute une cause, une conséquence ou une explication absente.

Ne confonds pas un fait inventé avec une courte appréciation
personnelle clairement identifiable.


=========================================================
4. PLAGIAT
=========================================================

Nombres, dates, noms, lieux, termes scientifiques et autres faits précis
peuvent rester identiques.

Signale un risque réel de plagiat seulement lorsqu'un passage reprend :
- une phrase entière ou presque entière ;
- la même construction avec presque les mêmes mots ;
- plusieurs expressions caractéristiques dans le même ordre ;
- une formulation clairement reconnaissable de la source.


=========================================================
5. CLARTÉ
=========================================================

Signale CLARTÉ uniquement si le passage est réellement :
- difficile à comprendre ;
- contradictoire ;
- ambigu au point de gêner le sens ;
- incohérent ;
- difficilement compréhensible à la première écoute.

Une phrase simple, scolaire ou imparfaite n'est pas un problème
si elle est compréhensible.


=========================================================
6. QUALITÉ RADIO
=========================================================

Il s'agit d'un seuil MINIMAL et non d'une recherche de perfection.

Pour 6e-5e :
accepte :
- phrases courtes ;
- vocabulaire simple ;
- organisation simple ;
- sélection de 2 ou 3 idées essentielles.

Une introduction est suffisante si :
- le sujet est identifiable ;
- au moins une information permet de comprendre son intérêt.

IMPORTANT :
une introduction correcte de niveau 6e-5e ne doit pas être rejetée
parce qu'elle n'explique pas encore un mécanisme, une cause,
un chiffre ou un détail qui peut naturellement être présenté
dans le développement.

Un développement est suffisant s'il permet de comprendre
quelques idées essentielles sélectionnées.

Une conclusion peut tenir en une phrase si elle apporte
une véritable idée de fin.

Pour 4e-3e :
attends davantage de précision, de liens et de développement.

Même en 4e-3e :
n'exige jamais l'exhaustivité.

Une idée peut être suffisamment expliquée par son principe essentiel.

N'exige pas une procédure technique complète simplement
parce qu'elle existe dans la source.

Un instrument, une étape opératoire, un chiffre
ou un détail de procédure ne doit devenir obligatoire
que si son absence empêche réellement de comprendre le principe.

Avant de signaler QUALITÉ RADIO INSUFFISANTE,
demande-toi :

« Ce passage empêche-t-il réellement un auditeur de ce niveau
de comprendre suffisamment l'idée,
ou est-ce que je souhaiterais seulement qu'il soit plus détaillé ? »

Si le passage pourrait simplement être meilleur :
NE LE SIGNALE PAS.


=========================================================
7. RÉFÉRENCES
=========================================================

Signale uniquement :
- références absentes ;
- information bibliographique essentielle disponible mais manquante ;
- référence fausse ;
- référence ne permettant pas d'identifier la source.

Si les références sont correctes :
ne les mentionne pas dans le retour.


=========================================================
8. DÉCISION
=========================================================

Pour chaque problème envisagé :

1. Quelle règle est réellement violée ?
2. La modification est-elle indispensable à la validation
   ou rendrait-elle seulement le texte meilleur ?

Si elle rendrait seulement la chronique meilleure :
NE SIGNALE PAS.

Si aucune correction obligatoire ne subsiste,
réponds EXACTEMENT :

VALIDÉ
La chronique peut passer à l'étape suivante.

Si au moins une correction obligatoire subsiste,
commence EXACTEMENT par :

À CORRIGER

Puis utilise uniquement ce format :

Problème : [PLAGIAT / INFORMATION NON FIDÈLE /
INFORMATION INVENTÉE / CLARTÉ /
QUALITÉ RADIO INSUFFISANTE / RÉFÉRENCE]

Passage concerné : "[citation exacte du passage de l'élève]"

Explication : [explication courte compréhensible par un collégien]

Consigne : [ce que l'élève doit vérifier ou corriger lui-même,
sans écrire la nouvelle formulation]

S'il existe plusieurs vrais problèmes, sépare-les.

Ne mentionne aucun élément correct.
Ne rédige jamais la correction.
"""

        contenu = f"""
NIVEAU DE L'ÉLÈVE :
{st.session_state.niveau}

FORMAT :
{st.session_state.nombre_voix}

SOURCE ORIGINALE :
{st.session_state.source}

CHRONIQUE COMPLÈTE DE L'ÉLÈVE :
{st.session_state.chronique}
"""

        try:

            with st.spinner(
                "Contrôle final de la chronique..."
            ):

                st.session_state.feedback_final = appel_ia(
                    instructions,
                    contenu
                )

            st.rerun()

        except Exception as e:

            st.error(
                "Une erreur s'est produite pendant le contrôle final."
            )

            st.code(str(e))

    else:

        if est_valide(
            st.session_state.feedback_final,
            "VALIDÉ"
        ):

            # -------------------------------------------------
            # CHRONIQUE VALIDÉE
            # -------------------------------------------------

            st.success("✅ Chronique validée")

            st.write(
                "La chronique a passé le contrôle final."
            )

            st.text_area(
                "Chronique validée :",
                value=st.session_state.chronique,
                height=420,
                disabled=True
            )

            st.divider()

            # -------------------------------------------------
            # PDF
            # -------------------------------------------------

            st.subheader("📄 PDF Radio ISTJ")

            st.write(
                "Ta chronique est prête. "
                "Tu peux maintenant générer sa version PDF prête à imprimer."
            )

            try:

                pdf = generer_pdf()

                st.download_button(
                    label="📥 Télécharger le PDF Radio ISTJ",
                    data=pdf,
                    file_name="chronique_radio_istj.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

                st.caption(
                    "Le PDF contient uniquement la chronique validée "
                    "et les références fournies par l'élève."
                )

            except Exception as e:

                st.error(
                    "Le PDF n'a pas pu être généré."
                )

                st.code(str(e))

        else:

            # -------------------------------------------------
            # CORRECTIONS APRÈS CONTRÔLE FINAL
            # -------------------------------------------------

            st.error(
                "La chronique doit encore être corrigée."
            )

            st.write(
                st.session_state.feedback_final
            )

            st.divider()

            st.write(
                "**Choisis la partie que tu dois corriger :**"
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button("Corriger l'introduction"):

                    st.session_state.feedback_introduction = ""
                    st.session_state.feedback_final = ""
                    st.session_state.etape = "introduction"

                    st.rerun()

                if st.button("Corriger la conclusion"):

                    st.session_state.feedback_conclusion = ""
                    st.session_state.feedback_final = ""
                    st.session_state.etape = "conclusion"

                    st.rerun()

            with col2:

                if st.button("Corriger le développement"):

                    st.session_state.feedback_developpement = ""
                    st.session_state.feedback_final = ""
                    st.session_state.etape = "developpement"

                    st.rerun()

                if st.button("Corriger les références"):

                    st.session_state.feedback_references = ""
                    st.session_state.feedback_final = ""
                    st.session_state.etape = "references"

                    st.rerun()
