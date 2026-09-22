import pandas as pd
import io
import requests

OWID_AGE_URL = "https://ourworldindata.org/grapher/cantril-ladder-age-groups.csv"

AGE_MID = {
    "Up to 29 years": 24.5,
    "30-44 years": 37.0,
    "45-59 years": 52.0,
    "60+ years": 70.0
}

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
        "30-44 years",
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

def fetch_wb(indicator_code, col_name):
    url = f"http://api.worldbank.org/v2/country/all/indicator/{indicator_code}?format=json&per_page=10000&date=2019:2023"
    resposta = requests.get(url).json()
    
    df = pd.DataFrame(resposta[1])
    df['iso3'] = df['countryiso3code']
    df = df.dropna(subset=['value'])
    df = df.sort_values('date', ascending=False).drop_duplicates('iso3')
    
    return df[['iso3', 'value']].rename(columns={'value': col_name})

def build_country_table():
    print("Baixando dados do Banco Mundial...")
    gdp = fetch_wb("NY.GDP.PCAP.PP.KD", "gdp_pc")
    pop = fetch_wb("SP.POP.TOTL", "pop")
    area = fetch_wb("AG.LND.TOTL.K2", "area_km2")
    
    df = gdp.merge(pop, on="iso3", how="outer").merge(area, on="iso3", how="outer")
    df = df[df['iso3'] != ""]
    
    return df.dropna(subset=["iso3"])