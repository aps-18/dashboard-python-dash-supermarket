#  # DEVOIR PYTHON AVANCÉ - Amélie Pires


#  ## Importation des bibliothèques

# %%
import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px


#  ## Chargement et préparation des données

# %%
df = pd.read_csv("data/supermarket_sales.csv").copy()

# Conversion date
df = df.assign(Date=pd.to_datetime(df["Date"], errors="coerce"))

# Suppression des dates manquantes
df = df.loc[df["Date"].notna()].copy()

# Création semaine
df = df.assign(Semaine=df["Date"].dt.to_period("W").apply(lambda x: x.start_time))


#  ## Initialisation de l'application Dash

# %%
app = dash.Dash(__name__)
app.title = "Dashboard Supermarket Sales"


#  ## Définition des couleurs du thème

# %%
orange = "#F28C28"
orange_fonce = "#D96C06"
orange_clair = "#FCE6D1"
fond = "#FFF4E8"
blanc = "#FFFFFF"
texte = "#2F2F2F"
rose = "#E78AC3"
bleu = "#4C78A8"


#  ## Construction du layout du tableau de bord

# %%
app.layout = html.Div(
    style={
        "backgroundColor": fond,
        "padding": "20px",
        "fontFamily": "Arial"
    },
    children=[

        html.Div(
            style={
                "backgroundColor": orange_fonce,
                "padding": "20px",
                "borderRadius": "15px",
                "marginBottom": "20px"
            },
            children=[
                html.H1(
                    "Tableau de bord interactif d’analyse des ventes du supermarché",
                    style={"color": "white", "textAlign": "center", "margin": "0"}
                ),
                html.P(
                    "Analyse des ventes selon le sexe et la ville",
                    style={"color": "white", "textAlign": "center", "marginTop": "10px"}
                )
            ]
        ),

        html.Div(
            style={
                "display": "flex",
                "gap": "20px",
                "marginBottom": "20px",
                "flexWrap": "wrap"
            },
            children=[

                html.Div(
                    style={
                        "backgroundColor": blanc,
                        "padding": "15px",
                        "borderRadius": "10px",
                        "flex": "1"
                    },
                    children=[
                        html.Label("Choisissez un sexe :", style={"fontWeight": "bold"}),
                        dcc.Dropdown(
                            id="filtre-sexe",
                            options=[
                                {"label": "Tous", "value": "Tous"},
                                {"label": "Female", "value": "Female"},
                                {"label": "Male", "value": "Male"}
                            ],
                            value="Tous",
                            clearable=False
                        )
                    ]
                ),

                html.Div(
                    style={
                        "backgroundColor": blanc,
                        "padding": "15px",
                        "borderRadius": "10px",
                        "flex": "1"
                    },
                    children=[
                        html.Label("Choisissez une ou plusieurs villes :", style={"fontWeight": "bold"}),
                        dcc.Dropdown(
                            id="filtre-ville",
                            options=[
                                {"label": ville, "value": ville}
                                for ville in sorted(df["City"].unique())
                            ],
                            value=[],
                            multi=True,
                            placeholder="Toutes les villes"
                        )
                    ]
                )
            ]
        ),

        html.Div(
            style={
                "display": "flex",
                "gap": "20px",
                "marginBottom": "20px",
                "flexWrap": "wrap"
            },
            children=[

                html.Div(
                    style={
                        "backgroundColor": blanc,
                        "padding": "20px",
                        "borderRadius": "10px",
                        "textAlign": "center",
                        "flex": "1",
                        "borderTop": f"5px solid {orange}",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.05)"
                    },
                    children=[
                        html.H3("Montant total des achats", style={"color": texte}),
                        html.H2(id="indicateur-total", style={"color": orange_fonce})
                    ]
                ),

                html.Div(
                    style={
                        "backgroundColor": blanc,
                        "padding": "20px",
                        "borderRadius": "10px",
                        "textAlign": "center",
                        "flex": "1",
                        "borderTop": f"5px solid {orange}",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.05)"
                    },
                    children=[
                        html.H3("Nombre total d’achats", style={"color": texte}),
                        html.H2(id="indicateur-nb", style={"color": orange_fonce})
                    ]
                )
            ]
        ),

        html.Div(
            style={
                "display": "flex",
                "gap": "20px",
                "marginBottom": "20px",
                "flexWrap": "wrap"
            },
            children=[

                html.Div(
                    style={
                        "backgroundColor": blanc,
                        "padding": "15px",
                        "borderRadius": "10px",
                        "flex": "2"
                    },
                    children=[
                        dcc.Graph(id="graph-histogramme")
                    ]
                ),

                html.Div(
                    style={
                        "backgroundColor": blanc,
                        "padding": "15px",
                        "borderRadius": "10px",
                        "flex": "1"
                    },
                    children=[
                        dcc.Graph(id="graph-circulaire")
                    ]
                )
            ]
        ),

        html.Div(
            style={
                "backgroundColor": blanc,
                "padding": "15px",
                "borderRadius": "10px"
            },
            children=[
                dcc.Graph(id="graph-evolution")
            ]
        )
    ]
)

#  ## Définition du callback interactif

# %%
@app.callback(
    Output("indicateur-total", "children"),
    Output("indicateur-nb", "children"),
    Output("graph-histogramme", "figure"),
    Output("graph-circulaire", "figure"),
    Output("graph-evolution", "figure"),
    Input("filtre-sexe", "value"),
    Input("filtre-ville", "value")
)
def update_dashboard(sexe, villes):

    dff = df.copy()

    # Filtre sexe
    if sexe != "Tous":
        dff = dff[dff["Gender"] == sexe]

    # Filtre ville
    if villes is not None and len(villes) > 0:
        dff = dff[dff["City"].isin(villes)]

    # Indicateurs
    montant_total = dff["Total"].sum()
    nb_achats = dff["Invoice ID"].count()

    indicateur_total = f"{montant_total:,.2f} $".replace(",", " ")
    indicateur_nb = f"{nb_achats}"

    # Histogramme
    fig_hist = px.histogram(
        dff,
        x="Total",
        color="Gender",
        facet_col="City",
        nbins=25,
        title="Répartition des montants totaux des achats par sexe et par ville",
        color_discrete_map={
            "Female": rose,
            "Male": bleu
        }
    )

    fig_hist.update_layout(
        template="simple_white",
        paper_bgcolor=blanc,
        plot_bgcolor=blanc,
        font_color=texte,
        title_font_color=orange_fonce
    )

    # Diagramme circulaire
    df_pie = dff.groupby("Product line", as_index=False)["Invoice ID"].count()
    df_pie = df_pie.rename(columns={"Invoice ID": "Nombre d'achats"})

    fig_pie = px.pie(
        df_pie,
        names="Product line",
        values="Nombre d'achats",
        title="Répartition de la catégorie de produit"
    )

    fig_pie.update_layout(
        template="simple_white",
        paper_bgcolor=blanc,
        font_color=texte,
        title_font_color=orange_fonce
    )

    # Evolution hebdomadaire
    df_line = dff.groupby(["Semaine", "City"], as_index=False)["Total"].sum()

    fig_line = px.line(
        df_line,
        x="Semaine",
        y="Total",
        color="City",
        markers=True,
        title="Évolution hebdomadaire du montant total des achats par ville"
    )

    fig_line.update_layout(
        template="simple_white",
        paper_bgcolor=blanc,
        plot_bgcolor=blanc,
        font_color=texte,
        title_font_color=orange_fonce,
        xaxis_title="Semaine",
        yaxis_title="Montant total des achats"
    )

    return indicateur_total, indicateur_nb, fig_hist, fig_pie, fig_line

# 

#  ## Lancement de l'application

# %%
server = app.server

if __name__ == "__main__":
    print("Dashboard disponible ici : http://127.0.0.1:8055/")
    app.run(debug=False, port=8055)


