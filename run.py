# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 18:46:43 2023
"""

import locale
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go

locale.setlocale(locale.LC_TIME, "us_US.UTF-8")


def read_data(file_path: str) -> None:
    """Read the excel data file and preprocesses it."""
    df = pd.read_excel(
        file_path,
        converters={
            "Baubeginn": pd.to_datetime,
            "erste Netzsynchronisation": pd.to_datetime,
            "Kommerzieller Betrieb": pd.to_datetime,
            "Abschaltung": pd.to_datetime,
            "Bau/Projekt eingestellt": pd.to_datetime,
        }
    )

    df["Jahr_Baubeginn"] = df["Baubeginn"].apply(
        lambda x: x.year if isinstance(x, pd.Timestamp) else None
    )

    df["Jahr_Inbetriebnahme"] = df["Kommerzieller Betrieb"].apply(
        lambda x: x.year if isinstance(x, pd.Timestamp) else None
    )

    df["Jahr_Abschaltung"] = df["Abschaltung"].apply(
        lambda x: x.year if isinstance(x, pd.Timestamp) else None
    )

    df["Bauzeit"] = df["Jahr_Inbetriebnahme"] - df["Jahr_Baubeginn"]

    return df


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Filter and compute the data and compute."""
    years = np.arange(1955, 2025)
    dct_length = []
    dct_power = []
    for year in years:
        data_year = df.loc[(df["Jahr_Inbetriebnahme"] <= year) &
                           ((df["Jahr_Abschaltung"] >= year) | (df["Jahr_Abschaltung"].isna()))]
        dct_power.append(data_year["Leistung, Netto in MW"].sum())
        dct_length.append(len(data_year))

    d = pd.DataFrame()
    d["years"] = years
    d.set_index("years", inplace=True)
    d["num"] = dct_length
    d["power"] = dct_power

    return d


def plot_data(df: pd.DataFrame) -> None:
    """Plot the number of operating nuclear reactors and their capacity."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['num'],
        name='Number of Operating Nuclear Reactors',
        mode='lines+markers',
        marker=dict(color='black'),
        hovertemplate="Number of Reactors: %{y}<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['power'] / 1000,
        name='Total Net Capacity',
        mode='lines+markers',
        marker=dict(color='#977073'),
        yaxis='y2',
        hovertemplate="Total Net Capacity: %{y:.0f} GW<extra></extra>",
    ))

    fig.update_layout(
        title="Evolution of Nuclear Power Plants in Europe:<br>Number of Operating Nuclear Reactors and Their Combined Net Capacity",
        xaxis=dict(title=None,
                   showgrid=True, gridwidth=1, gridcolor='rgba(128, 128, 128, 0.1)'),
        yaxis=dict(title="Number of Operating Nuclear Reactors",
                   showgrid=True, gridwidth=1, gridcolor='rgba(128, 128, 128, 0.1)'),
        yaxis2=dict(title="Net Capacity in GW", overlaying='y',
                    side='right', showgrid=False),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(family="Roboto", color="black", size=12),
        hovermode='x unified',
        hoverlabel=dict(font=dict(size=12)),
        legend=dict(x=0.95, y=0.05,
                    xanchor='right', yanchor='bottom'),
        width=997,
        height=580,
    )

    # Save the plot as an HTML file
    fig.write_html("index.html")

    # Show the figure
    fig.show()


def main():
    """Execute the script."""
    FILE_NAME = "nuclear_power_plants.xlsx"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "data", FILE_NAME)

    # Read and preprocess the data
    df = read_data(FILE_PATH)

    # Process the data
    data = process_data(df)

    # Plot the data
    plot_data(data)


if __name__ == "__main__":
    main()
