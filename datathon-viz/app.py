import marimo

__generated_with = "0.23.10"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import altair as alt

    import data_loading
    import metrics

    return alt, data_loading, metrics, mo


@app.cell
def _(mo):
    mo.md("""
    # Affaire Ultia x CNC - analyse du corpus

    Dynamique de la tempete virale sur X (19 mars - 1 mai 2026).
    Les visualisations alimentent la grille d'analyse en 5 axes.
    """)
    return


@app.cell
def _(data_loading):
    corpus = data_loading.load_corpus()
    debut, fin = data_loading.period_bounds(corpus)
    return corpus, debut, fin


@app.cell
def _(corpus, debut, fin, mo):
    mo.md(f"""
    **Messages** : {len(corpus)} &nbsp; **Auteurs uniques** : {corpus["Author"].nunique()}
    &nbsp; **Periode** : {debut:%Y-%m-%d} au {fin:%Y-%m-%d}
    """)
    return


@app.cell
def _(corpus, metrics, mo):
    jour_pic, volume_pic = metrics.peak_day(corpus)
    cartes_cles = mo.hstack(
        [
            mo.stat(metrics.message_count(corpus), label="Messages", bordered=True),
            mo.stat(metrics.author_count(corpus), label="Auteurs uniques", bordered=True),
            mo.stat(
                f"{metrics.type_share(corpus, 'RETWEET'):.0%}",
                label="Retweets",
                bordered=True,
            ),
            mo.stat(
                f"{jour_pic:%d/%m}",
                label="Jour de pic",
                caption=f"{volume_pic} messages",
                bordered=True,
            ),
            mo.stat(
                f"{metrics.peak_concentration(corpus, 4):.0%}",
                label="Volume sur 4 jours de pic",
                bordered=True,
            ),
        ],
        gap=1,
    )
    cartes_cles
    return


@app.cell
def _(mo):
    mo.md("""
    ## Propagation
    """)
    return


@app.cell
def _(mo):
    granularite = mo.ui.dropdown(
        options=["1h", "3h", "1D"], value="1h", label="Granularite de la timeline"
    )
    granularite
    return (granularite,)


@app.cell
def _(alt, corpus, granularite, metrics):
    serie = metrics.timeline(corpus, granularite.value)
    evenements = metrics.key_events()

    courbe = (
        alt.Chart(serie)
        .mark_line()
        .encode(
            x=alt.X("time:T", title="Date"),
            y=alt.Y("count:Q", title="Messages"),
        )
    )
    regles = (
        alt.Chart(evenements)
        .mark_rule(color="firebrick", strokeDash=[4, 4])
        .encode(x="date:T", tooltip=alt.Tooltip("label:N", title="Evenement"))
    )
    etiquettes = (
        alt.Chart(evenements)
        .mark_text(align="left", angle=270, dx=4, color="firebrick", fontSize=10)
        .encode(x="date:T", y=alt.value(0), text="label:N")
    )
    timeline_annotee = (courbe + regles + etiquettes).properties(
        title="Volume de messages dans le temps (evenements annotes)",
        width="container",
        height=320,
    )
    timeline_annotee
    return


@app.cell
def _(mo):
    mo.md("""
    La courbe explose le 27/03, juste apres le clip de @TwitchGauchiste (26/03) :
    l'emballement suit l'etincelle a un jour pres. Un second pic accompagne la
    suspension du fonds (08/04). 86 % des messages sont des retweets : la dynamique
    est massivement de la rediffusion, pas du debat.
    """)
    return


@app.cell
def _(alt, corpus, metrics):
    repartition = metrics.engagement_breakdown(corpus)
    barres_type = (
        alt.Chart(repartition)
        .mark_bar()
        .encode(
            x=alt.X("count:Q", title="Messages"),
            y=alt.Y("engagement_type:N", sort="-x", title="Type"),
        )
        .properties(
            title="Repartition par type de message",
            width="container",
            height=200,
        )
    )
    barres_type
    return


@app.cell
def _(mo):
    mo.md("""
    ## Acteurs
    """)
    return


@app.cell
def _(alt, corpus, metrics):
    auteurs = metrics.top_authors(corpus, 15)
    barres_auteurs = (
        alt.Chart(auteurs)
        .mark_bar()
        .encode(
            x=alt.X("count:Q", title="Messages"),
            y=alt.Y("author:N", sort="-x", title="Auteur"),
        )
        .properties(
            title="Comptes les plus actifs",
            width="container",
            height=400,
        )
    )
    barres_auteurs
    return


@app.cell
def _(alt, corpus, metrics):
    amplifies = metrics.top_amplified(corpus, 15)
    barres_amplifies = (
        alt.Chart(amplifies)
        .mark_bar()
        .encode(
            x=alt.X("count:Q", title="Retweets recus"),
            y=alt.Y("author:N", sort="-x", title="Auteur"),
        )
        .properties(
            title="Comptes les plus amplifies",
            width="container",
            height=400,
        )
    )
    barres_amplifies
    return


@app.cell
def _(alt, corpus, metrics):
    certifies = metrics.verified_breakdown(corpus)
    barres_certifies = (
        alt.Chart(certifies)
        .mark_bar()
        .encode(
            x=alt.X("count:Q", title="Messages"),
            y=alt.Y("statut:N", sort="-x", title="Statut du compte"),
        )
        .properties(
            title="Messages par statut de compte (certifie ou non)",
            width="container",
            height=160,
        )
    )
    barres_certifies
    return


@app.cell
def _(alt, corpus, metrics):
    audience = metrics.top_by_reach(corpus, 15)
    barres_reach = (
        alt.Chart(audience)
        .mark_bar()
        .encode(
            x=alt.X("reach:Q", title="Reach cumule"),
            y=alt.Y("author:N", sort="-x", title="Auteur"),
        )
        .properties(
            title="Comptes a la plus grande audience (reach cumule)",
            width="container",
            height=400,
        )
    )
    barres_reach
    return


@app.cell
def _(mo):
    mo.md("""
    Les comptes les plus actifs sont surtout non certifies : la vague est portee par
    des anonymes, pas par des medias. Le top des comptes amplifies, lui, est nettement
    marque politiquement. Comparer le volume de messages et le reach cumule separe les
    comptes bruyants (beaucoup de messages) des comptes a forte audience.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Semantique
    """)
    return


@app.cell
def _(alt, corpus, metrics):
    sentiment = metrics.sentiment_over_time(corpus, "1D")
    aire_sentiment = (
        alt.Chart(sentiment)
        .mark_area()
        .encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("count:Q", title="Part des messages", stack="normalize"),
            color=alt.Color("Sentiment:N", title="Sentiment"),
        )
        .properties(
            title="Evolution du sentiment dans le temps",
            width="container",
            height=300,
        )
    )
    aire_sentiment
    return


@app.cell
def _(mo):
    mo.md("""
    Le sentiment reste majoritairement neutre (66 %) avec une part negative forte
    (31 %). Cet axe s'appuie sur la colonne fournie ; une mesure d'agressivite plus
    fine demanderait un agent dedie.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Narratifs (premiere approche par hashtags)
    """)
    return


@app.cell
def _(alt, corpus, metrics):
    hashtags = metrics.top_hashtags(corpus, 15)
    barres_hashtags = (
        alt.Chart(hashtags)
        .mark_bar()
        .encode(
            x=alt.X("count:Q", title="Occurrences"),
            y=alt.Y("hashtag:N", sort="-x", title="Hashtag"),
        )
        .properties(
            title="Hashtags les plus frequents",
            width="container",
            height=400,
        )
    )
    barres_hashtags
    return


@app.cell
def _(mo):
    mo.md("""
    Les hashtags sont peu representatifs ici : #ultia n'apparait que 177 fois et des
    tags hors-sujet (#racketfiscal) remontent via un tweet viral. La crise se joue
    surtout en retweets bruts, sans hashtag. Le vrai classement des narratifs passera
    par un agent de classification (etape suivante).
    """)
    return


if __name__ == "__main__":
    app.run()
