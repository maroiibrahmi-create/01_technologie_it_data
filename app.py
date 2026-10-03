import io
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Dashboard Support IT",
    page_icon="📊",
    layout="wide",
)


# -----------------------------
# Data loading and preparation
# -----------------------------
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        source = uploaded_file
    else:
        candidates = [
            Path("01_Technologie_IT.xlsx"),
            Path("data/01_Technologie_IT.xlsx"),
        ]
        source = next((p for p in candidates if p.exists()), None)
        if source is None:
            return None

    df = pd.read_excel(source, sheet_name="Données", skiprows=2)
    df.columns = [str(c).strip() for c in df.columns]

    df["Date ouverture"] = pd.to_datetime(df["Date ouverture"], errors="coerce")

    numeric_cols = [
        "Réponse (h)",
        "Résolution (h)",
        "Objectif SLA (h)",
        "Satisfaction /5",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Mois"] = df["Date ouverture"].dt.to_period("M").dt.to_timestamp()

    # SLA is evaluated ONLY for resolved tickets.
    df["SLA dépassé"] = pd.NA
    resolved_mask = df["Statut"].eq("Résolu")
    df.loc[resolved_mask, "SLA dépassé"] = (
        df.loc[resolved_mask, "Résolution (h)"]
        > df.loc[resolved_mask, "Objectif SLA (h)"]
    )

    return df


def format_hours(value):
    if pd.isna(value):
        return "—"
    return f"{value:.1f} h"


def pct(value):
    if pd.isna(value):
        return "—"
    return f"{value:.1%}"


def answer_questions(df):
    resolved = df[df["Statut"].eq("Résolu")].copy()

    # Q1
    q1 = (
        df["Type de demande"]
        .value_counts()
        .rename_axis("Type de demande")
        .reset_index(name="Tickets")
    )

    # Q2
    q2 = (
        df.groupby("Service")
        .agg(
            Tickets=("ID ticket", "count"),
            Delai_median_resolution=("Résolution (h)", "median"),
        )
        .sort_values("Tickets", ascending=False)
    )

    # Q3
    q3 = (
        resolved.groupby("Priorité")["SLA dépassé"]
        .agg(Tickets_resolus="count", Depassements="sum", Taux="mean")
        .sort_index()
    )

    # Q4
    q4 = (
        df.groupby("Canal")["Réponse (h)"]
        .agg(Tickets="count", Mediane="median", Moyenne="mean")
        .sort_values("Mediane")
    )

    # Q5
    monthly_volume = (
        df.groupby("Mois")
        .size()
        .rename("Volume")
    )

    monthly_sla = (
        resolved.groupby("Mois")["SLA dépassé"]
        .agg(Depassements="sum", Tickets_resolus="count", Taux="mean")
    )

    q5 = pd.concat([monthly_volume, monthly_sla], axis=1).fillna(0).reset_index()

    return q1, q2, q3, q4, q5


# -----------------------------
# Charts
# -----------------------------
def chart_q1(q1):
    fig, ax = plt.subplots(figsize=(8, 4.2))
    q = q1.sort_values("Tickets")
    ax.barh(q["Type de demande"], q["Tickets"])
    ax.set_title("Q1 — Volume par type de demande")
    ax.set_xlabel("Nombre de tickets")
    ax.set_ylabel("")
    for i, v in enumerate(q["Tickets"]):
        ax.text(v + 2, i, str(v), va="center")
    fig.tight_layout()
    return fig


def chart_q3(q3):
    fig, ax = plt.subplots(figsize=(8, 4.2))
    x = q3.index
    y = q3["Taux"] * 100
    ax.bar(x, y)
    ax.set_title("Q3 — Taux de dépassement SLA par priorité")
    ax.set_ylabel("Tickets dépassant le SLA (%)")
    ax.set_ylim(0, max(60, y.max() + 10))
    for i, v in enumerate(y):
        ax.text(i, v + 1, f"{v:.1f}%", ha="center")
    fig.tight_layout()
    return fig


def chart_q4(q4):
    fig, ax = plt.subplots(figsize=(8, 4.2))
    x = q4.index
    y = q4["Mediane"]
    ax.bar(x, y)
    ax.set_title("Q4 — Délai médian de première réponse par canal")
    ax.set_ylabel("Heures")
    for i, v in enumerate(y):
        ax.text(i, v + 0.2, f"{v:.1f} h", ha="center")
    fig.tight_layout()
    return fig


def chart_q5(q5):
    fig, ax1 = plt.subplots(figsize=(9, 4.5))

    ax1.plot(
        q5["Mois"],
        q5["Volume"],
        marker="o",
        linewidth=2,
        label="Volume de tickets",
    )
    ax1.set_xlabel("Mois")
    ax1.set_ylabel("Nombre de tickets")
    ax1.tick_params(axis="x", rotation=45)

    ax2 = ax1.twinx()
    ax2.plot(
        q5["Mois"],
        q5["Taux"] * 100,
        marker="s",
        linestyle="--",
        linewidth=2,
        label="Taux de dépassement SLA",
    )
    ax2.set_ylabel("Dépassement SLA (%)")

    ax1.set_title("Q5 — Évolution mensuelle du volume et des dépassements SLA")
    fig.tight_layout()
    return fig


# -----------------------------
# App
# -----------------------------
st.title("📊 Dashboard — Support informatique")
st.caption("Entreprise de services numériques fictive · Janvier–Août 2026")

with st.sidebar:
    st.header("Données")
    uploaded = st.file_uploader(
        "Importer le fichier Excel",
        type=["xlsx"],
        help="Le fichier doit contenir une feuille nommée « Données ».",
    )

    st.divider()
    st.header("Filtres")

df = load_data(uploaded)

if df is None:
    st.warning(
        "Aucun fichier Excel n'a été trouvé. Placez « 01_Technologie_IT.xlsx » "
        "à côté de app.py ou importez-le avec le bouton de la barre latérale."
    )
    st.stop()

# Sidebar filters
with st.sidebar:
    villes = sorted(df["Ville"].dropna().unique())
    services = sorted(df["Service"].dropna().unique())
    canaux = sorted(df["Canal"].dropna().unique())
    priorites = sorted(df["Priorité"].dropna().unique())
    types = sorted(df["Type de demande"].dropna().unique())
    statuts = sorted(df["Statut"].dropna().unique())

    selected_villes = st.multiselect("Ville", villes, default=villes)
    selected_services = st.multiselect("Service", services, default=services)
    selected_canaux = st.multiselect("Canal", canaux, default=canaux)
    selected_priorites = st.multiselect("Priorité", priorites, default=priorites)
    selected_types = st.multiselect("Type de demande", types, default=types)
    selected_statuts = st.multiselect("Statut", statuts, default=statuts)

    min_date = df["Date ouverture"].min().date()
    max_date = df["Date ouverture"].max().date()
    date_range = st.date_input(
        "Période",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = df[
    df["Ville"].isin(selected_villes)
    & df["Service"].isin(selected_services)
    & df["Canal"].isin(selected_canaux)
    & df["Priorité"].isin(selected_priorites)
    & df["Type de demande"].isin(selected_types)
    & df["Statut"].isin(selected_statuts)
    & df["Date ouverture"].dt.date.between(start_date, end_date)
].copy()

q1, q2, q3, q4, q5 = answer_questions(filtered)

resolved = filtered[filtered["Statut"].eq("Résolu")].copy()
total = len(filtered)
resolved_count = len(resolved)
open_count = total - resolved_count
sla_rate = resolved["SLA dépassé"].mean() if resolved_count else float("nan")
median_response = filtered["Réponse (h)"].median() if total else float("nan")

# -----------------------------
# FIRST PAGE / MAIN DASHBOARD
# -----------------------------
st.header("1. Réponses aux questions")

# KPI cards
c1, c2, c3, c4 = st.columns(4)
c1.metric("Tickets sélectionnés", f"{total:,}")
c2.metric("Tickets résolus", f"{resolved_count:,}")
c3.metric("Tickets en cours", f"{open_count:,}")
c4.metric("Dépassement SLA", pct(sla_rate))

st.divider()

# Q1
st.subheader("Q1. Quels types de demandes représentent le plus de tickets ?")
if not q1.empty:
    top_type = q1.iloc[0]
    st.write(
        f"Le type de demande le plus représenté est **{top_type['Type de demande']}**, "
        f"avec **{int(top_type['Tickets'])} tickets**."
    )
    col1, col2 = st.columns([1.3, 1])
    with col1:
        st.pyplot(chart_q1(q1), use_container_width=True)
    with col2:
        st.dataframe(q1, hide_index=True, use_container_width=True)
else:
    st.info("Aucune donnée pour les filtres sélectionnés.")

# Q2
st.subheader("Q2. Quel service reçoit le plus de tickets et quel est son délai médian de résolution ?")
if not q2.empty:
    top_service = q2.index[0]
    top_service_volume = int(q2.iloc[0]["Tickets"])
    top_service_median = q2.iloc[0]["Delai_median_resolution"]
    st.write(
        f"Le service recevant le plus de tickets est **{top_service}** "
        f"avec **{top_service_volume} tickets**. "
        f"Son délai médian de résolution est de **{format_hours(top_service_median)}** "
        f"(calculé sur les tickets ayant une durée de résolution renseignée)."
    )
    display_q2 = q2.rename(
        columns={
            "Tickets": "Tickets",
            "Delai_median_resolution": "Délai médian résolution (h)",
        }
    ).reset_index(names="Service")
    st.dataframe(
        display_q2.style.format({"Délai médian résolution (h)": "{:.1f}"}),
        hide_index=True,
        use_container_width=True,
    )

# Q3
st.subheader("Q3. Quelle part des tickets résolus dépasse l’objectif SLA ? Comparez par priorité.")
if not q3.empty:
    overall = resolved["SLA dépassé"].mean() if len(resolved) else float("nan")
    st.write(
        f"Sur les tickets **résolus uniquement**, le taux global de dépassement SLA est "
        f"de **{pct(overall)}**. Le dénominateur est donc le nombre de tickets résolus "
        f"pour chaque priorité."
    )
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.pyplot(chart_q3(q3), use_container_width=True)
    with col2:
        display_q3 = q3.reset_index().rename(
            columns={
                "Tickets_resolus": "Tickets résolus",
                "Depassements": "Dépassements SLA",
                "Taux": "Taux de dépassement",
            }
        )
        st.dataframe(
            display_q3.style.format({"Taux de dépassement": "{:.1%}"}),
            hide_index=True,
            use_container_width=True,
        )

# Q4
st.subheader("Q4. Les canaux d’entrée diffèrent-ils en temps de première réponse ?")
if not q4.empty:
    fastest = q4.index[0]
    slowest = q4.index[-1]
    st.write(
        f"Les délais médians observés diffèrent selon le canal : **{fastest}** est à "
        f"{format_hours(q4.loc[fastest, 'Mediane'])}, contre "
        f"{format_hours(q4.loc[slowest, 'Mediane'])} pour **{slowest}**. "
        "Cette comparaison est descriptive : elle ne démontre pas qu’un canal cause "
        "à lui seul un meilleur ou moins bon délai, car d’autres facteurs peuvent intervenir."
    )
    st.pyplot(chart_q4(q4), use_container_width=True)

# Q5
st.subheader("Q5. Comment le volume de tickets et les dépassements SLA évoluent-ils par mois ?")
if not q5.empty:
    st.pyplot(chart_q5(q5), use_container_width=True)
    display_q5 = q5.copy()
    display_q5["Mois"] = display_q5["Mois"].dt.strftime("%Y-%m")
    display_q5 = display_q5.rename(
        columns={
            "Mois": "Mois",
            "Volume": "Volume tickets",
            "Depassements": "Dépassements SLA",
            "Tickets_resolus": "Tickets résolus",
            "Taux": "Taux dépassement",
        }
    )
    st.dataframe(
        display_q5.style.format({"Taux dépassement": "{:.1%}"}),
        hide_index=True,
        use_container_width=True,
    )

# Q6
st.subheader("Q6. Quelle action concrète proposer au responsable du support ?")
if not q3.empty and not q5.empty and not q2.empty:
    overall = resolved["SLA dépassé"].mean() if len(resolved) else float("nan")
    worst_priority = q3["Taux"].idxmax()
    worst_priority_rate = q3.loc[worst_priority, "Taux"]
    busiest_service = q2.index[0]
    busiest_service_volume = int(q2.iloc[0]["Tickets"])
    peak_month_row = q5.loc[q5["Volume"].idxmax()]
    peak_month = peak_month_row["Mois"].strftime("%B %Y")
    peak_volume = int(peak_month_row["Volume"])

    st.info(
        f"**Action proposée : mettre en place un suivi prioritaire des tickets à risque SLA**, "
        f"avec une revue régulière du service **{busiest_service}** ({busiest_service_volume} tickets) "
        f"et de la priorité **{worst_priority}**, dont le taux de dépassement est de "
        f"**{worst_priority_rate:.1%}**. Le taux global de dépassement est de **{overall:.1%}** "
        f"sur les tickets résolus. Le volume atteint son maximum en **{peak_month}** "
        f"({peak_volume} tickets), ce qui peut justifier un renfort ou une surveillance "
        "accrue pendant les périodes de forte charge."
    )
    st.caption(
        "Cette recommandation est fondée uniquement sur les indicateurs descriptifs du tableau "
        "et doit être complétée par une analyse des causes avant toute décision opérationnelle."
    )

st.divider()

# -----------------------------
# Exploration page/section
# -----------------------------
st.header("2. Exploration des données")
st.write(
    "Les filtres de la barre latérale s'appliquent à tous les indicateurs et graphiques."
)

tab1, tab2, tab3 = st.tabs(["Vue par service", "Vue par priorité", "Données filtrées"])

with tab1:
    service_view = (
        filtered.groupby("Service")
        .agg(
            Tickets=("ID ticket", "count"),
            Resolution_mediane_h=("Résolution (h)", "median"),
            Reponse_mediane_h=("Réponse (h)", "median"),
            Satisfaction_moyenne=("Satisfaction /5", "mean"),
        )
        .sort_values("Tickets", ascending=False)
        .reset_index()
    )
    st.dataframe(
        service_view.style.format(
            {
                "Resolution_mediane_h": "{:.1f}",
                "Reponse_mediane_h": "{:.1f}",
                "Satisfaction_moyenne": "{:.2f}",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

with tab2:
    priority_view = (
        filtered.groupby("Priorité")
        .agg(
            Tickets=("ID ticket", "count"),
            Resolution_mediane_h=("Résolution (h)", "median"),
            Reponse_mediane_h=("Réponse (h)", "median"),
        )
        .reset_index()
    )
    resolved_priority = (
        filtered[filtered["Statut"].eq("Résolu")]
        .groupby("Priorité")["SLA dépassé"]
        .mean()
        .rename("Taux_SLA_depasse")
        .reset_index()
    )
    priority_view = priority_view.merge(resolved_priority, on="Priorité", how="left")
    st.dataframe(
        priority_view.style.format(
            {
                "Resolution_mediane_h": "{:.1f}",
                "Reponse_mediane_h": "{:.1f}",
                "Taux_SLA_depasse": "{:.1%}",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

with tab3:
    st.dataframe(filtered, hide_index=True, use_container_width=True)
    csv = filtered.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Télécharger les données filtrées (CSV)",
        data=csv,
        file_name="tickets_filtrés.csv",
        mime="text/csv",
    )

st.caption(
    "Définition SLA : Résolution (h) > Objectif SLA (h), uniquement pour les tickets résolus. "
    "Les valeurs vides des tickets en cours ne sont jamais traitées comme zéro."
)
