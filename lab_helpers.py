import pandas as pd
import io
import requests

OWID_AGE_URL = "https://ourworldindata.org/grapher/cantril-ladder-age-groups.csv"

def load_owid_age_data():
    """Carrega e prepara os dados de felicidade da OWID por faixa etária."""

    response = requests.get(
        OWID_AGE_URL,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    response.raise_for_status()

    df = pd.read_csv(io.BytesIO(response.content))

    df = df.melt(
        id_vars=["Entity", "Code", "Year"],
        var_name="Age_Group",
        value_name="Happiness",
    )

    df = sort_by_country_and_age_group(df)

    df = df.dropna(subset=["Code"])

    df = df.rename(
        columns={
            "Entity": "country",
            "Code": "iso3",
            "Year": "year",
        }
    )

    return df


def sort_by_country_and_age_group(df):
    """Define a ordem das faixas etárias e ordena os dados."""

    age_order = [
        "Up to 29 years",
        "30-44 year",
        "45-59 years",
        "60+ years",
    ]

    df["Age_Group"] = pd.Categorical(
        df["Age_Group"],
        categories=age_order,
        ordered=True,
    )

    return df.sort_values(
        ["Entity", "Age_Group"],
    )

def build_country_table():
  pass