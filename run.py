# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 18:46:43 2023
"""

import locale
from datetime import datetime
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go

locale.setlocale(locale.LC_TIME, "us_US.UTF-8")


# Define a dictionary of colors for each country
COUNTRY_COLORS = {
    "Austria": "#FF00FF",
    "Belarus": "#0072b1",
    "Belgium": "#e6a000",
    "Bulgaria": "#bfef45",
    "Czech Republic": "#c4022b",
    "Finland": "#9300d3",
    "France": "#000000",
    "Germany": "#d45e00",
    "Hungary": "#FFD700",
    "Italy": "#5d5a5a",
    "Lithuania": "#FA8072",
    "Netherlands": "#9e9e00",
    "Poland" : "#CCCCFF",
    "Romania": "#a65959",
    "Slovakia": "#36648B",
    "Slovenia": "#7DF9FF",
    "Spain": "#c0c0c0",
    "Sweden": "#2ca02c",
    "Switzerland": "#c400a4",
    "Turkey": "#9FE2BF",
    "Ukraine": "#48066f",
    "United Kingdom": "#ff0000"
}


def read_data(file_path: str) -> None:
    """Read the excel data file and preprocesses it."""
    return pd.read_excel(
        file_path,
        converters={
            "Baubeginn": pd.to_datetime,
            "erste Netzsynchronisation": pd.to_datetime,
            "Kommerzieller Betrieb": pd.to_datetime,
            "Abschaltung": pd.to_datetime,
            "Bau/Projekt eingestellt": pd.to_datetime
            }
        )


def conditions(row, date_limit):
    is_operational = row["Kommerzieller Betrieb"] <= date_limit
    is_shutdown = row["Abschaltung"] >= date_limit
    is_shutdown_unknown = pd.isnull(row["Abschaltung"])

    return is_operational and (is_shutdown or is_shutdown_unknown)


def process_data(df: pd.DataFrame) -> dict:
    """Filter and compute the data."""
    df = df.copy()
    df["Leistung, Netto in MW"] /= 1000

    years = np.arange(1955, 2024)
    result = {}
    for year in years:
        mask = df.apply(conditions, axis=1, date_limit=datetime(year, 12, 31))
        data_year = df.loc[mask]

        # Group the installed capacity of reactors per country
        data_year_grouped = data_year[["Land", "Leistung, Netto in MW" ]].groupby(by=["Land"]).sum()
        data_year_grouped.name = "capacity of reactors"

        result[year] = data_year_grouped
    return result


def plot_data(data: dict) -> None:
    """Plot the number of operating nuclear reactors and their capacity."""
    fig = go.Figure()

    # Get unique country names
    countries = set()
    for df in data.values():
        countries.update(df.index.unique())
    countries = sorted(countries)

    for country in countries:
        y_values = [df.loc[country, 'Leistung, Netto in MW'] if country in df.index else 0 for df in data.values()]
        fig.add_trace(go.Bar(
            x=list(data.keys()),
            y=y_values,
            name=country,
            marker=dict(
                color=COUNTRY_COLORS[country],
                line=dict(width=0),
                showscale=False,
                opacity=1
            ),
            hovertemplate="%{y:.2f} GW"
        ))

    fig.update_layout(
        title="Evolution of Nuclear Power Plants in Europe:<br>Total Net Capacity of Operating Nuclear Reactors by Country and Year",
        xaxis=dict(title=None,
                   showgrid=True, gridwidth=1, gridcolor="rgba(128, 128, 128, 0.1)"),
        yaxis=dict(
            title="Net Capacity of Operating Nuclear Reactors in GW",
            showgrid=True, gridwidth=1, gridcolor="rgba(128, 128, 128, 0.1)",
            range=[-5, 165]
            ),
        barmode="stack",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(family="sans-serif", color="black", size=12),
        hovermode="x unified",
        hoverlabel=dict(font=dict(size=12)),
        width=997,
        height=580,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="center",
            x=0.5,
            traceorder="normal",
            tracegroupgap=20,
            font=dict(size=10),
            itemwidth=60
            )
        )

    # Save the plot as an HTML file
    fig.write_html("index.html")

    # Show the figure
    fig.show()


def main() -> None:
    """Execute the script."""
    FILE_NAME = "nuclear_power_plants.xlsx"
    # FILE_PATH = os.path.join(os.path.dirname(__file__), "data", FILE_NAME)

    FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ee-nuclear-commissioning", "data", FILE_NAME))

    # Read and preprocess the data
    df = read_data(FILE_PATH)

    # Process the data
    data = process_data(df)

    # Plot the data
    plot_data(data)


if __name__ == "__main__":
    main()
