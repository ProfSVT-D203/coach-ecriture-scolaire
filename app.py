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


def contexte_documentaire():
    """
    Renvoie le corpus documentaire utilisé pour vérifier les faits.
    """

    if st.session_state.parcours == "guide":
        return st.session_state.source

    return f"""
THÈME :
{st.session_state.libre_theme}

SUJET :
{st.session_state.libre_sujet}

ANGLE :
{st.session_state.libre_angle}

RECHERCHES / DOCUMENTS / NOTES :
{st.session_state.libre_recherches}

INFORMATIONS RETENUES PAR L'ÉLÈVE :
{st.session_state.libre_infos}
"""


def references_affichees():
    if st.session_state.parcours == "guide":
        return (
            f"Auteur : {st.session_state.ref_auteur.strip()}\n"
            f"Titre : {st.session_state.ref_titre.strip()}\n"
            f"Média : {st.session_state.ref_media.strip()}\n"
            f"Date : {st.session_state.ref_date.strip()}"
        )

    return st.session_state.libre_references.strip()


def assembler_chronique():

    parties = [
        st.session_state.introduction.strip(),
        st.session_state.developpement.strip(),
        st.session_state.conclusion.strip(),
        "",
        "Références :",
        references_affichees(),
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
# PDF
# =========================================================

def texte_pdf(texte):

    texte = str(texte)

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
        fontSize=10.5,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"),
        spaceAfter=16
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

    elements.append(
        Paragraph(
            "RADIO ISTJ",
            style_radio
        )
    )

    parcours_pdf = (
        "Parcours guidé"
        if st.session_state.parcours == "guide"
        else "Parcours libre"
    )

    elements.append(
        Paragraph(
            f"Chronique élève - {parcours_pdf} - version validée",
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

    if st.session_state.parcours == "libre":

        elements.append(
            Paragraph(
                f"<b>Sujet :</b> {texte_pdf(st.session_state.libre_sujet)}",
                style_sous_titre
            )
        )

    elements.append(Spacer(1, 0.2 * cm))

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

    bloc_references = [
        Paragraph(
            "Références",
            style_section
        ),
        Paragraph(
            texte_pdf(references_affichees()),
            style_reference
        )
    ]

    elements.append(
        KeepTogether(bloc_references)
    )

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

initialiser("parcours", "")
initialiser("niveau", "6e-5e")
initialiser("nombre_voix", "1 voix")

# Parcours guidé
initialiser("source")
initialiser("sujet")
initialiser("idees")
initialiser("vocabulaire")
initialiser("feedback_comprehension")

# Parcours libre
initialiser("libre_theme")
initialiser("libre_sujet")
initialiser("libre_angle")
initialiser("feedback_angle")

initialiser("libre_recherches")
initialiser("libre_infos")
initialiser("feedback_recherches")

initialiser("libre_what")
initialiser("libre_who")
initialiser("libre_where")
initialiser("libre_when")
initialiser("libre_whyhow")

# Plan commun
initialiser("plan_introduction")
initialiser("plan_developpement")
initialiser("plan_conclusion")
initialiser("plan_repartition")
initialiser("feedback_plan")

# Rédaction commune
initialiser("introduction")
initialiser("feedback_introduction")

initialiser("developpement")
initialiser("feedback_developpement")

initialiser("conclusion")
initialiser("feedback_conclusion")

# Références guidées
initialiser("ref_auteur")
initialiser("ref_titre")
initialiser("ref_media")
initialiser("ref_date")

# Références libres
initialiser("libre_references")

initialiser("feedback_references")

# Final
initialiser("chronique")
initialiser("feedback_final")


# =========================================================
# RÈGLES COMMUNES DE RÉDACTION
# =========================================================

REGLES_REDACTION = """
Tu es le Coach d'écriture pédagogique de Radio ISTJ.

Tu accompagnes un élève de collège qui écrit lui-même
une chronique destinée à être entendue à la radio.

RÈGLE ABSOLUE :
L'élève est l'auteur.

Tu ne dois JAMAIS :
- écrire une phrase de chronique à sa place ;
- proposer une reformulation prête à copier ;
- écrire une introduction modèle ;
- écrire une conclusion modèle ;
- donner un début ou une fin de phrase ;
- rédiger une transition ;
- rédiger une réplique à sa place ;
- fournir une version améliorée du texte.

Tu peux :
- analyser ;
- questionner ;
- signaler UNE difficulté ;
- rappeler une règle d'écriture radio ;
- donner quelques mots-clés si nécessaire.

RÈGLES RADIO À UTILISER COMME RÉFÉRENTIEL :

COURT :
- privilégier les phrases courtes ;
- une phrase porte de préférence une idée.

CLAIR :
- le texte doit être compris à la première écoute ;
- les liens logiques doivent rester compréhensibles.

CONCIS :
- utiliser des mots précis ;
- éviter les détours inutiles.

L'accroche doit donner envie d'écouter.

L'écriture peut aussi être descriptive,
créer des images mentales et penser aux sons,
mais ces éléments ne sont jamais obligatoires
dans toutes les chroniques.

NE TRANSFORME PAS ces conseils en grille rigide.

Une chronique simple mais claire peut être excellente.

FIDÉLITÉ :
Tu travailles uniquement à partir des documents et recherches
fournis par l'élève dans l'application.

N'ajoute aucune connaissance extérieure.

SÉLECTIONNER N'EST PAS DÉFORMER.

Une chronique n'est jamais obligée de reprendre
toutes les informations disponibles.

NIVEAU 6e-5e :
- phrases simples acceptées ;
- vocabulaire simple accepté ;
- organisation simple acceptée ;
- quelques idées correctement traitées peuvent suffire.

NIVEAU 4e-3e :
attends davantage :
- de précision ;
- de liens ;
- d'explications ;
- de progression logique.

Mais jamais d'exhaustivité.

SI UNE CORRECTION EST NÉCESSAIRE :
- commence par ce qui fonctionne ;
- choisis UNE seule difficulté prioritaire ;
- ne fournis pas la correction ;
- pose UNE question ciblée ;
- laisse l'élève reformuler lui-même.

Ne cherche pas la perfection.
Cherche un seuil suffisant pour une chronique radio de collège.
"""


# =========================================================
# TITRE
# =========================================================

st.title("🎙️ Coach d'écriture Radio ISTJ")


# =========================================================
# ACCUEIL
# =========================================================

if st.session_state.etape == "accueil":

    st.write(
        "Prépare ta chronique radio étape par étape."
    )

    st.divider()

    niveau = st.radio(
        "Quel est ton niveau ?",
        ["6e-5e", "4e-3e"],
        horizontal=True
    )

    nombre_voix = st.radio(
        "Combien de voix pour la chronique ?",
        ["1 voix", "2 voix", "3 voix"],
        horizontal=True
    )

    st.divider()

    st.subheader("Comment veux-tu préparer ta chronique ?")

    parcours = st.radio(
        "Choisis ton parcours :",
        [
            "📄 Parcours guidé — Je pars d'une source",
            "💡 Parcours libre — Je pars d'une idée"
        ]
    )

    if parcours.startswith("📄"):

        st.info(
            "Tu as déjà un article ou un document. "
            "Le Coach t'aide à le comprendre, construire ton plan "
            "et rédiger ta chronique."
        )

        source = st.text_area(
            "Colle ici l'article ou la source :",
            height=300
        )

        if st.button("Commencer le parcours guidé"):

            if not source.strip():

                st.warning(
                    "Tu dois d'abord fournir une source."
                )

            else:

                st.session_state.parcours = "guide"
                st.session_state.niveau = niveau
                st.session_state.nombre_voix = nombre_voix
                st.session_state.source = source
                st.session_state.etape = "comprehension"

                st.rerun()

    else:

        st.info(
            "Tu pars d'une idée ou d'un thème. "
            "Le Coach t'aide à préciser ton sujet, choisir ton angle, "
            "organiser tes recherches et écrire pour la radio."
        )

        if st.button("Commencer le parcours libre"):

            st.session_state.parcours = "libre"
            st.session_state.niveau = niveau
            st.session_state.nombre_voix = nombre_voix
            st.session_state.etape = "libre_cadrage"

            st.rerun()


# =========================================================
# PARCOURS GUIDÉ — COMPRÉHENSION
# =========================================================

elif st.session_state.etape == "comprehension":

    st.subheader("Étape 1 — Comprendre la source")

    st.write(
        f"**Niveau :** {st.session_state.niveau}  \n"
        f"**Format :** {st.session_state.nombre_voix}"
    )

    sujet = st.text_area(
        "Quel est le sujet principal ?",
        value=st.session_state.sujet
    )

    idees = st.text_area(
        "Quelles sont les 2 ou 3 idées importantes ?",
        value=st.session_state.idees,
        height=160
    )

    vocabulaire = st.text_area(
        "Y a-t-il un mot ou un passage que tu ne comprends pas ? "
        "Si tout est clair, écris : Aucun.",
        value=st.session_state.vocabulaire
    )

    if st.button("Continuer"):

        if not sujet.strip() or not idees.strip() or not vocabulaire.strip():

            st.warning(
                "Complète les trois parties avant de continuer."
            )

        else:

            st.session_state.sujet = sujet
            st.session_state.idees = idees
            st.session_state.vocabulaire = vocabulaire

            invalider_apres("comprehension")

            st.session_state.etape = "analyse_comprehension"

            st.rerun()


elif st.session_state.etape == "analyse_comprehension":

    st.subheader("Compréhension enregistrée")

    st.write("### Sujet principal")
    st.write(st.session_state.sujet)

    st.write("### Idées importantes")
    st.write(st.session_state.idees)

    st.write("### Mots ou passages difficiles")
    st.write(st.session_state.vocabulaire)

    if st.button("Modifier mes réponses"):
        st.session_state.etape = "comprehension"
        st.rerun()

    st.divider()

    if not st.session_state.feedback_comprehension:

        if st.button("🤖 Vérifier ma compréhension"):

            instructions = """
Tu vérifies uniquement la compréhension d'une source
par un élève de collège.

Vérifie :
- le sujet principal ;
- les 2 ou 3 idées retenues ;
- les éventuels mots ou passages incompris.

SÉLECTIONNER N'EST PAS DÉFORMER.

Une idée exacte ne doit pas être critiquée
simplement parce que la source permettrait d'en dire davantage.

Si l'élève signale un mot incompris,
explique-le simplement.

Si une erreur importante subsiste :
- ne donne pas la correction ;
- choisis UNE difficulté ;
- pose UNE question permettant à l'élève
  de retrouver lui-même l'information.

Si tout est suffisant, réponds exactement :

COMPRÉHENSION VALIDÉE
Tu as bien compris les idées essentielles de la source.
Tu peux passer à la construction du plan.

Sinon commence exactement par :

À REVOIR
"""

            contenu = f"""
NIVEAU :
{st.session_state.niveau}

SOURCE :
{st.session_state.source}

SUJET :
{st.session_state.sujet}

IDÉES :
{st.session_state.idees}

VOCABULAIRE :
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

            if st.button("Construire mon plan"):
                st.session_state.etape = "plan"
                st.rerun()

        else:

            st.subheader("Retour du Coach")
            st.write(st.session_state.feedback_comprehension)

            if st.button("Reprendre mes réponses"):
                st.session_state.etape = "comprehension"
                st.rerun()


# =========================================================
# PARCOURS LIBRE — THÈME / SUJET / ANGLE
# =========================================================

elif st.session_state.etape == "libre_cadrage":

    st.subheader("Étape 1 — De l'idée à l'angle")

    st.write(
        "Pars du général pour aller vers quelque chose de précis."
    )

    with st.expander("📻 Rappel : thème, sujet et angle"):

        st.write(
            "**Thème** : le domaine général. "
            "Exemples : sport, musique, environnement, sciences."
        )

        st.write(
            "**Sujet** : un aspect précis de ce thème."
        )

        st.write(
            "**Angle** : le point de vue choisi, "
            "c'est-à-dire ce que tu veux vraiment faire comprendre "
            "ou découvrir à ton auditeur."
        )

        st.warning(
            "Une chronique ne peut pas tout raconter. "
            "Choisir un angle, c'est choisir l'essentiel."
        )

    libre_theme = st.text_input(
        "Quel est ton thème général ?",
        value=st.session_state.libre_theme
    )

    libre_sujet = st.text_input(
        "Quel sujet précis veux-tu traiter ?",
        value=st.session_state.libre_sujet
    )

    libre_angle = st.text_area(
        "Quel angle veux-tu choisir ? "
        "Qu'est-ce que tu veux surtout faire comprendre ou découvrir ?",
        value=st.session_state.libre_angle,
        height=120
    )

    if st.button("Enregistrer mon idée"):

        if not all([
            libre_theme.strip(),
            libre_sujet.strip(),
            libre_angle.strip()
        ]):

            st.warning(
                "Complète le thème, le sujet et l'angle."
            )

        else:

            st.session_state.libre_theme = libre_theme
            st.session_state.libre_sujet = libre_sujet
            st.session_state.libre_angle = libre_angle
            st.session_state.feedback_angle = ""

            st.session_state.etape = "libre_angle_verif"

            st.rerun()


elif st.session_state.etape == "libre_angle_verif":

    st.subheader("Ton projet de chronique")

    st.write(f"**Thème :** {st.session_state.libre_theme}")
    st.write(f"**Sujet :** {st.session_state.libre_sujet}")
    st.write(f"**Angle :** {st.session_state.libre_angle}")

    if st.button("Modifier mon projet"):
        st.session_state.etape = "libre_cadrage"
        st.rerun()

    st.divider()

    if not st.session_state.feedback_angle:

        if st.button("🤖 Vérifier mon angle"):

            instructions = """
Tu es le Coach d'écriture Radio ISTJ.

Tu vérifies uniquement la relation :

THÈME → SUJET → ANGLE.

Le thème est général.
Le sujet est un aspect du thème.
L'angle est l'aspect particulier ou le message principal
que l'élève veut faire comprendre.

Un angle ne doit pas simplement répéter le sujet.

Mais ne cherche pas forcément un angle original ou spectaculaire.

Un angle simple et clair convient à un collégien.

Tu ne proposes PAS toi-même un angle prêt à utiliser.

Si l'angle est trop large :
pose UNE question qui aide l'élève à le préciser.

Si thème, sujet et angle forment un ensemble suffisamment précis,
réponds exactement :

ANGLE VALIDÉ
Ton sujet et ton angle sont suffisamment précis.
Tu peux commencer tes recherches.

Sinon commence exactement par :

À REVOIR
"""

            contenu = f"""
NIVEAU :
{st.session_state.niveau}

THÈME :
{st.session_state.libre_theme}

SUJET :
{st.session_state.libre_sujet}

ANGLE :
{st.session_state.libre_angle}
"""

            try:

                with st.spinner(
                    "Le Coach examine ton angle..."
                ):

                    st.session_state.feedback_angle = appel_ia(
                        instructions,
                        contenu
                    )

                st.rerun()

            except Exception as e:
                st.error("Erreur pendant la vérification.")
                st.code(str(e))

    else:

        if est_valide(
            st.session_state.feedback_angle,
            "ANGLE VALIDÉ"
        ):

            st.success("✅ Angle validé")

            if st.button("Passer aux recherches"):
                st.session_state.etape = "libre_recherches"
                st.rerun()

        else:

            st.subheader("Retour du Coach")
            st.write(st.session_state.feedback_angle)

            if st.button("Revoir mon angle"):
                st.session_state.etape = "libre_cadrage"
                st.rerun()


# =========================================================
# PARCOURS LIBRE — RECHERCHES
# =========================================================

elif st.session_state.etape == "libre_recherches":

    st.subheader("Étape 2 — Faire mes recherches")

    st.write(
        "Rassemble maintenant les informations qui pourront servir "
        "à ta chronique."
    )

    st.info(
        "Tu peux utiliser plusieurs sources. "
        "Copie ici tes notes, extraits utiles et références."
    )

    libre_recherches = st.text_area(
        "Mes recherches et mes sources :",
        value=st.session_state.libre_recherches,
        height=320
    )

    libre_infos = st.text_area(
        "Quelles informations veux-tu surtout retenir pour ta chronique ?",
        value=st.session_state.libre_infos,
        height=180
    )

    if st.button("Enregistrer mes recherches"):

        if not libre_recherches.strip():

            st.warning(
                "Ajoute au moins une source ou des notes de recherche."
            )

        elif not libre_infos.strip():

            st.warning(
                "Indique les informations que tu souhaites retenir."
            )

        else:

            st.session_state.libre_recherches = libre_recherches
            st.session_state.libre_infos = libre_infos
            st.session_state.feedback_recherches = ""

            st.session_state.etape = "libre_recherches_verif"

            st.rerun()


elif st.session_state.etape == "libre_recherches_verif":

    st.subheader("Informations retenues")

    st.write(st.session_state.libre_infos)

    if st.button("Modifier mes recherches"):
        st.session_state.etape = "libre_recherches"
        st.rerun()

    st.divider()

    if not st.session_state.feedback_recherches:

        if st.button("🤖 Vérifier mes recherches"):

            instructions = """
Tu vérifies le travail de recherche préparatoire
d'un élève pour une chronique radio.

Utilise UNIQUEMENT les documents et notes fournis.

Vérifie principalement :

1. que les informations que l'élève veut retenir
   sont justifiables par ses recherches ;

2. qu'elles correspondent à son angle ;

3. qu'il dispose d'assez de matière pour commencer à organiser
   sa chronique.

SÉLECTIONNER N'EST PAS DÉFORMER.

L'élève n'a pas à utiliser toutes les informations trouvées.

Ne rédige jamais la chronique à sa place.

Si une information retenue n'est pas soutenue par les recherches :
pose UNE question ciblée.

Si le dossier est suffisant, réponds exactement :

RECHERCHES VALIDÉES
Tes recherches donnent suffisamment d'informations pour préparer ta chronique.

Sinon commence exactement par :

À REVOIR
"""

            contenu = f"""
NIVEAU :
{st.session_state.niveau}

THÈME :
{st.session_state.libre_theme}

SUJET :
{st.session_state.libre_sujet}

ANGLE :
{st.session_state.libre_angle}

RECHERCHES :
{st.session_state.libre_recherches}

INFORMATIONS RETENUES :
{st.session_state.libre_infos}
"""

            try:

                with st.spinner(
                    "Le Coach vérifie tes recherches..."
                ):

                    st.session_state.feedback_recherches = appel_ia(
                        instructions,
                        contenu
                    )

                st.rerun()

            except Exception as e:
                st.error("Erreur pendant la vérification.")
                st.code(str(e))

    else:

        if est_valide(
            st.session_state.feedback_recherches,
            "RECHERCHES VALIDÉES"
        ):

            st.success("✅ Recherches validées")

            if st.button("Préparer les informations essentielles"):
                st.session_state.etape = "libre_5w"
                st.rerun()

        else:

            st.subheader("Retour du Coach")
            st.write(st.session_state.feedback_recherches)

            if st.button("Reprendre mes recherches"):
                st.session_state.etape = "libre_recherches"
                st.rerun()


# =========================================================
# PARCOURS LIBRE — 5W
# =========================================================

elif st.session_state.etape == "libre_5w":

    st.subheader("Étape 3 — Les informations essentielles")

    st.write(
        "Les journalistes utilisent souvent les 5 W pour vérifier "
        "qu'ils disposent des informations utiles."
    )

    st.warning(
        "Ce n'est pas un questionnaire obligatoire : "
        "si une question n'est pas utile à ton angle, tu peux écrire "
        "« Pas nécessaire pour mon angle »."
    )

    libre_what = st.text_area(
        "WHAT ? De quoi parle précisément ta chronique ?",
        value=st.session_state.libre_what
    )

    libre_who = st.text_area(
        "WHO ? Qui est concerné ?",
        value=st.session_state.libre_who
    )

    libre_where = st.text_area(
        "WHERE ? Où cela se passe-t-il ?",
        value=st.session_state.libre_where
    )

    libre_when = st.text_area(
        "WHEN ? Quand cela se passe-t-il ?",
        value=st.session_state.libre_when
    )

    libre_whyhow = st.text_area(
        "WHY / HOW ? Pourquoi ce sujet est-il intéressant ? "
        "Que veux-tu expliquer ou faire comprendre ?",
        value=st.session_state.libre_whyhow,
        height=130
    )

    if st.button("Enregistrer cette préparation"):

        st.session_state.libre_what = libre_what
        st.session_state.libre_who = libre_who
        st.session_state.libre_where = libre_where
        st.session_state.libre_when = libre_when
        st.session_state.libre_whyhow = libre_whyhow

        st.session_state.etape = "plan"

        st.rerun()


# =========================================================
# PLAN — COMMUN AUX DEUX PARCOURS
# =========================================================

elif st.session_state.etape == "plan":

    st.subheader("Construire le plan")

    if st.session_state.parcours == "libre":

        st.info(
            f"**Sujet :** {st.session_state.libre_sujet}\n\n"
            f"**Angle :** {st.session_state.libre_angle}"
        )

        with st.expander("📻 Rappel : écrire pour la radio"):

            st.write(
                "**Court, clair, concis.** "
                "Privilégie les phrases courtes et les idées faciles "
                "à comprendre à la première écoute."
            )

            st.write(
                "Ton introduction peut comporter une **accroche** "
                "qui donne envie de rester à l'écoute."
            )

            st.write(
                "Ton développement doit rester centré sur ton **angle**."
            )

            st.write(
                "Ta conclusion doit apporter une vraie idée de fin."
            )

    else:

        st.write(
            "Indique ce que tu veux faire dans chaque partie. "
            "Tu n'écris pas encore les phrases."
        )

    plan_introduction = st.text_area(
        "Introduction — Que veux-tu faire au début ?",
        value=st.session_state.plan_introduction
    )

    plan_developpement = st.text_area(
        "Développement — Quelles idées veux-tu présenter, et dans quel ordre ?",
        value=st.session_state.plan_developpement,
        height=180
    )

    plan_conclusion = st.text_area(
        "Conclusion — Sur quelle idée veux-tu terminer ?",
        value=st.session_state.plan_conclusion
    )

    if st.session_state.nombre_voix != "1 voix":

        plan_repartition = st.text_area(
            f"Répartition des {st.session_state.nombre_voix} — "
            "Qui intervient dans les différentes parties ?",
            value=st.session_state.plan_repartition,
            height=140
        )

    else:
        plan_repartition = ""

    if st.button("Enregistrer mon plan"):

        if not all([
            plan_introduction.strip(),
            plan_developpement.strip(),
            plan_conclusion.strip()
        ]):

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

    if st.button("Modifier mon plan"):
        st.session_state.etape = "plan"
        st.rerun()

    st.divider()

    if not st.session_state.feedback_plan:

        if st.button("🤖 Faire vérifier mon plan"):

            instructions = """
Tu vérifies le plan d'une chronique Radio ISTJ.

Le plan peut être simple.

Vérifie :
- introduction ;
- développement ;
- conclusion ;
- cohérence avec le sujet ;
- cohérence avec l'angle s'il existe ;
- répartition des voix si nécessaire.

Le plan n'est PAS le texte définitif.

Tu ne rédiges aucune phrase à la place de l'élève.

SÉLECTIONNER N'EST PAS DÉFORMER.

Pour 6e-5e :
un plan simple peut suffire.

Pour 4e-3e :
attends davantage de précision et de progression,
sans exiger l'exhaustivité.

Si l'élève suit un parcours libre,
vérifie particulièrement que le développement reste centré
sur l'ANGLE choisi.

Si le plan est suffisant, réponds exactement :

PLAN VALIDÉ
Ton plan est suffisamment clair et organisé.
Tu peux commencer la rédaction de l'introduction.

Sinon commence exactement par :

À REVOIR

Puis traite UNE difficulté prioritaire.
"""

            contenu = f"""
NIVEAU :
{st.session_state.niveau}

FORMAT :
{st.session_state.nombre_voix}

PARCOURS :
{st.session_state.parcours}

DOCUMENTS / RECHERCHES :
{contexte_documentaire()}

PLAN INTRODUCTION :
{st.session_state.plan_introduction}

PLAN DÉVELOPPEMENT :
{st.session_state.plan_developpement}

PLAN CONCLUSION :
{st.session_state.plan_conclusion}

RÉPARTITION :
{st.session_state.plan_repartition}
"""

            try:

                with st.spinner(
                    "Le Coach vérifie ton plan..."
                ):

                    st.session_state.feedback_plan = appel_ia(
                        instructions,
                        contenu
                    )

                st.rerun()

            except Exception as e:
                st.error("Erreur pendant la vérification.")
                st.code(str(e))

    else:

        if est_valide(
            st.session_state.feedback_plan,
            "PLAN VALIDÉ"
        ):

            st.success("✅ Plan validé")

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
# INTRODUCTION — COMMUNE
# =========================================================

elif st.session_state.etape == "introduction":

    st.subheader("Rédiger l'introduction")

    if st.session_state.parcours == "libre":

        st.info(
            "Pense à l'écoute : ton début doit permettre de comprendre "
            "le sujet et, si possible, donner envie d'écouter la suite."
        )

    else:

        st.info(
            "L'introduction doit permettre d'identifier le sujet "
            "et de comprendre son intérêt."
        )

    st.write("### Ton plan")
    st.write(st.session_state.plan_introduction)

    introduction = st.text_area(
        "Ton introduction :",
        value=st.session_state.introduction,
        height=180
    )

    if st.button("Enregistrer mon introduction"):

        if not introduction.strip():
            st.warning("Écris d'abord ton introduction.")

        else:
            st.session_state.introduction = introduction
            invalider_apres("introduction")
            st.session_state.etape = "controle_introduction"
            st.rerun()


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

Elle doit :
- permettre d'identifier le sujet ;
- permettre de comprendre son intérêt.

Dans le parcours libre,
vérifie aussi qu'elle reste cohérente avec l'angle.

Une accroche intéressante est un PLUS,
mais ne refuse pas automatiquement une introduction simple
si elle remplit déjà son rôle.

Pour 6e-5e :
une ou deux phrases simples peuvent suffire.

Ne demande pas automatiquement :
- date ;
- chiffre ;
- lieu plus précis ;
- mécanisme ;
- détail technique ;
- explication qui pourra venir dans le développement.

Pour 4e-3e :
tu peux attendre davantage de contextualisation,
mais l'introduction n'a pas à contenir le développement.

Si elle est suffisante, réponds exactement :

INTRODUCTION VALIDÉE
L'introduction remplit son rôle.
Tu peux passer au développement.

Sinon commence exactement par :

À REVOIR
"""

            contenu = f"""
NIVEAU :
{st.session_state.niveau}

PARCOURS :
{st.session_state.parcours}

FORMAT :
{st.session_state.nombre_voix}

DOCUMENTS / RECHERCHES :
{contexte_documentaire()}

PLAN :
{st.session_state.plan_introduction}

INTRODUCTION :
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
# DÉVELOPPEMENT — COMMUN
# =========================================================

elif st.session_state.etape == "developpement":

    st.subheader("Rédiger le développement")

    if st.session_state.parcours == "libre":

        st.info(
            f"Reste centré sur ton angle : "
            f"**{st.session_state.libre_angle}**"
        )

    st.write("### Ton plan")
    st.write(st.session_state.plan_developpement)

    if st.session_state.nombre_voix != "1 voix":

        st.write("### Répartition prévue")
        st.write(st.session_state.plan_repartition)

    developpement = st.text_area(
        "Ton développement :",
        value=st.session_state.developpement,
        height=340
    )

    if st.button("Enregistrer mon développement"):

        if not developpement.strip():
            st.warning("Écris d'abord ton développement.")

        else:
            st.session_state.developpement = developpement
            invalider_apres("developpement")
            st.session_state.etape = "controle_developpement"
            st.rerun()


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

Le PLAN est le contrat principal de rédaction.

Le développement n'a pas à reprendre
toutes les informations disponibles.

Vérifie :
- fidélité aux recherches ;
- idées prévues dans le plan ;
- clarté à l'écoute ;
- formulation personnelle ;
- cohérence avec l'angle dans le parcours libre.

Pour le parcours libre :
l'élève peut avoir davantage de liberté de ton,
de structure, de description et de transitions.

Ne transforme pas cette liberté en obligation.

IMPORTANT :

Le mot « comment » dans un plan
ne signifie pas automatiquement
« décrire toute la procédure technique ».

Une explication du principe peut suffire.

Pour 6e-5e :
quelques informations simples et exactes peuvent suffire.

Pour 4e-3e :
attends davantage de précision et d'explication.

RÈGLE D'ARRÊT :

Si toutes les idées prévues sont présentes,
fidèles et suffisamment expliquées,
tu DOIS valider.

Ne demande pas ensuite un chiffre,
un exemple, un instrument,
une étape ou un détail simplement
parce qu'il existe dans les recherches.

Si le développement est suffisant, réponds exactement :

DÉVELOPPEMENT VALIDÉ
Le développement remplit son rôle.
Tu peux passer à la conclusion.

Sinon commence exactement par :

À REVOIR

Traite UNE difficulté prioritaire.
"""

            contenu = f"""
NIVEAU :
{st.session_state.niveau}

PARCOURS :
{st.session_state.parcours}

FORMAT :
{st.session_state.nombre_voix}

DOCUMENTS / RECHERCHES :
{contexte_documentaire()}

PLAN :
{st.session_state.plan_developpement}

RÉPARTITION :
{st.session_state.plan_repartition}

DÉVELOPPEMENT :
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
# CONCLUSION — COMMUNE
# =========================================================

elif st.session_state.etape == "conclusion":

    st.subheader("Rédiger la conclusion")

    st.write("### Ton plan")
    st.write(st.session_state.plan_conclusion)

    conclusion = st.text_area(
        "Ta conclusion :",
        value=st.session_state.conclusion,
        height=180
    )

    if st.button("Enregistrer ma conclusion"):

        if not conclusion.strip():
            st.warning("Écris d'abord ta conclusion.")

        else:
            st.session_state.conclusion = conclusion
            invalider_apres("conclusion")
            st.session_state.etape = "controle_conclusion"
            st.rerun()


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

Elle doit apporter une vraie idée de fin.

Elle peut :
- rappeler l'essentiel ;
- ouvrir sur une perspective ;
- présenter un enjeu ;
- montrer une incertitude ;
- donner une courte appréciation personnelle identifiable.

Pour 6e-5e :
une phrase simple peut suffire.

Dans le parcours libre :
elle doit rester cohérente avec l'angle choisi.

Ne demande pas une information supplémentaire
simplement pour enrichir le texte.

Si elle est suffisante, réponds exactement :

CONCLUSION VALIDÉE
La conclusion apporte une véritable idée de fin.
Tu peux passer aux références.

Sinon commence exactement par :

À REVOIR
"""

            contenu = f"""
NIVEAU :
{st.session_state.niveau}

PARCOURS :
{st.session_state.parcours}

DOCUMENTS / RECHERCHES :
{contexte_documentaire()}

PLAN :
{st.session_state.plan_conclusion}

CONCLUSION :
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
# RÉFÉRENCES
# =========================================================

elif st.session_state.etape == "references":

    st.subheader("Références")

    if st.session_state.parcours == "guide":

        st.write(
            "Retrouve toi-même les références dans la source."
        )

        st.info(
            "Si une information n'est pas indiquée, "
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
                    "Complète les quatre champs."
                )

            else:

                st.session_state.ref_auteur = ref_auteur
                st.session_state.ref_titre = ref_titre
                st.session_state.ref_media = ref_media
                st.session_state.ref_date = ref_date

                invalider_apres("references")

                st.session_state.etape = "controle_references"

                st.rerun()

    else:

        st.write(
            "Indique les sources réellement utilisées pour ta chronique."
        )

        st.info(
            "Tu peux avoir plusieurs sources. "
            "Indique assez d'informations pour pouvoir les retrouver : "
            "auteur ou organisme, titre, média/site, date, lien si tu l'as."
        )

        libre_references = st.text_area(
            "Mes références :",
            value=st.session_state.libre_references,
            height=220
        )

        if st.button("Enregistrer mes références"):

            if not libre_references.strip():

                st.warning(
                    "Indique au moins une référence."
                )

            else:

                st.session_state.libre_references = libre_references

                invalider_apres("references")

                st.session_state.etape = "controle_references"

                st.rerun()


elif st.session_state.etape == "controle_references":

    st.subheader("Tes références")
    st.write(references_affichees())

    if st.button("Modifier mes références"):
        st.session_state.etape = "references"
        st.rerun()

    st.divider()

    if not st.session_state.feedback_references:

        if st.button("🤖 Vérifier mes références"):

            instructions = """
Tu vérifies uniquement les références d'une chronique.

Compare les références avec les documents et recherches
fournis par l'élève.

Dans le parcours guidé :
vérifie auteur, titre, média et date.

Dans le parcours libre :
plusieurs sources sont possibles.
Vérifie surtout que les sources citées correspondent
aux recherches utilisées et permettent raisonnablement
de retrouver les documents.

Tu ne fabriques pas de référence à la place de l'élève.

Si tout est suffisant, réponds exactement :

RÉFÉRENCES VALIDÉES
Les références correspondent aux sources utilisées.

Sinon commence exactement par :

À REVOIR
"""

            contenu = f"""
PARCOURS :
{st.session_state.parcours}

DOCUMENTS / RECHERCHES :
{contexte_documentaire()}

RÉFÉRENCES :
{references_affichees()}
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
# ASSEMBLAGE
# =========================================================

elif st.session_state.etape == "chronique_assemblee":

    st.subheader("Chronique assemblée")

    st.success(
        "La chronique a été assemblée uniquement "
        "avec les textes que tu as écrits."
    )

    st.text_area(
        "Ta chronique complète :",
        value=st.session_state.chronique,
        height=460,
        disabled=True
    )

    if st.button("🔎 Lancer le contrôle final"):
        st.session_state.etape = "controle_final"
        st.rerun()


# =========================================================
# CONTRÔLE FINAL
# =========================================================

elif st.session_state.etape == "controle_final":

    st.subheader("Contrôle final")

    if not st.session_state.feedback_final:

        instructions = """
Tu réalises le CONTRÔLE FINAL INDÉPENDANT
d'une chronique Radio ISTJ.

Tu ne réécris rien.
Tu ne cherches pas à améliorer le texte.

Tu vérifies uniquement les problèmes qui rendent
une correction réellement nécessaire.

Vérifie :

1. FIDÉLITÉ
Toute information factuelle doit être justifiable
par les documents et recherches fournis.

SÉLECTIONNER N'EST PAS DÉFORMER.

L'omission d'informations n'est pas une erreur.

2. INFORMATION INVENTÉE
Signale un fait qui n'apparaît pas dans les recherches
et ne peut pas raisonnablement en être déduit.

3. EXACTITUDE
Vérifie les nombres, dates, lieux, noms et données présentes.

4. PLAGIAT
Les faits précis peuvent être identiques.
Signale seulement une reprise vraiment trop proche
d'une phrase ou construction de la source.

5. CLARTÉ
Signale uniquement ce qui gêne réellement
la compréhension à la première écoute.

6. QUALITÉ RADIO
Utilise un seuil minimal :
court, clair, concis.

Une phrase simple ou scolaire n'est pas un problème
si elle reste compréhensible.

Dans le parcours libre :
vérifie également que la chronique reste globalement
cohérente avec l'angle choisi.

Ne transforme pas les principes journalistiques
en grille rigide.

Une accroche spectaculaire, des images mentales
ou un habillage sonore sont des possibilités,
pas des obligations.

7. NIVEAU

6e-5e :
accepte un texte simple et quelques idées essentielles.

4e-3e :
attends davantage de précision et d'explication,
sans exiger l'exhaustivité.

Avant de signaler un problème demande-toi :

« Cette correction est-elle indispensable,
ou rendrait-elle seulement la chronique meilleure ? »

Si elle rendrait seulement le texte meilleur :
NE LA SIGNALE PAS.

Si aucune correction obligatoire ne subsiste,
réponds EXACTEMENT :

VALIDÉ
La chronique peut passer à l'étape suivante.

Sinon commence EXACTEMENT par :

À CORRIGER

Puis utilise :

Problème : [type]

Passage concerné : "[citation exacte]"

Explication : [courte]

Consigne : [ce que l'élève doit corriger lui-même]

Ne rédige jamais la correction.
"""

        contenu = f"""
NIVEAU :
{st.session_state.niveau}

PARCOURS :
{st.session_state.parcours}

FORMAT :
{st.session_state.nombre_voix}

DOCUMENTS / RECHERCHES :
{contexte_documentaire()}

CHRONIQUE :
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
            st.error("Erreur pendant le contrôle final.")
            st.code(str(e))

    else:

        if est_valide(
            st.session_state.feedback_final,
            "VALIDÉ"
        ):

            st.success("✅ Chronique validée")

            st.write(
                "La chronique a passé le contrôle final."
            )

            st.text_area(
                "Chronique validée :",
                value=st.session_state.chronique,
                height=430,
                disabled=True
            )

            st.divider()

            st.subheader("📄 PDF Radio ISTJ")

            try:

                pdf = generer_pdf()

                st.download_button(
                    label="📥 Télécharger le PDF Radio ISTJ",
                    data=pdf,
                    file_name="chronique_radio_istj.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            except Exception as e:

                st.error(
                    "Le PDF n'a pas pu être généré."
                )

                st.code(str(e))

        else:

            st.error(
                "La chronique doit encore être corrigée."
            )

            st.write(
                st.session_state.feedback_final
            )

            st.divider()

            st.write(
                "**Choisis la partie à corriger :**"
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
