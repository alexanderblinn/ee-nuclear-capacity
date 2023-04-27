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


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Filter and compute the data and compute."""
    years = np.arange(1955, 2024)
    lst_length = []
    lst_power = []
    for year in years:
        data_year = df.loc[
            (df["Kommerzieller Betrieb"] <= datetime(year, 12, 31)) &
            ((df["Abschaltung"] >= datetime(year, 12, 31)) | (df["Abschaltung"].isna()))]
        lst_power.append(data_year["Leistung, Netto in MW"].sum())
        lst_length.append(len(data_year))

    d = pd.DataFrame()
    d["years"] = years
    d.set_index("years", inplace=True)
    d["num"] = lst_length
    d["power"] = lst_power

    return d


def plot_data(df: pd.DataFrame) -> None:
    """Plot the number of operating nuclear reactors and their capacity."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["num"],
        name="Number of Operating Nuclear Reactors",
        mode="lines+markers",
        marker=dict(color="black"),
        hovertemplate="Number of Reactors: %{y}<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["power"] / 1000,
        name="Total Net Capacity",
        mode="lines+markers",
        marker=dict(color="#977073"),
        yaxis="y2",
        hovertemplate="Total Net Capacity: %{y:.2f} GW<extra></extra>",
    ))

    # Add line at y=0
    fig.add_shape(
        dict(type="line", xref="paper", x0=0, x1=1, yref="y", y0=0, y1=0, line=dict(color="rgba(128, 128, 128, 0.1)", width=1))
    )

    fig.update_layout(
        title="Evolution of Nuclear Power Plants in Europe:<br>Number of Operating Nuclear Reactors and Their Combined Net Capacity",
        xaxis=dict(title=None,
                   showgrid=True, gridwidth=1, gridcolor="rgba(128, 128, 128, 0.1)"),
        yaxis=dict(title="Number of Operating Nuclear Reactors",
                   showgrid=True, gridwidth=1, gridcolor="rgba(128, 128, 128, 0.1)"),
        yaxis2=dict(title="Net Capacity in GW", overlaying="y",
                    side="right", showgrid=False),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(family="Droid Serif, serif", color="black", size=12),
        hovermode="x unified",
        hoverlabel=dict(font=dict(size=12)),
        legend=dict(x=0.95, y=0.05,
                    xanchor="right", yanchor="bottom"),
        width=997,
        height=580
    )

    # Save the plot as an HTML file
    fig.write_html("index.html")

    # Show the figure
    fig.show()


def main() -> None:
    """Execute the script."""
    FILE_NAME = "nuclear_power_plants.xlsx"
    # FILE_PATH = os.path.join(os.path.dirname(__file__), "data", FILE_NAME)

    FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "nuclear_reactors_europe_bubble", "data", FILE_NAME))

    # Read and preprocess the data
    df = read_data(FILE_PATH)

    # Process the data
    data = process_data(df)

    # Plot the data
    plot_data(data)


if __name__ == "__main__":
    main()
