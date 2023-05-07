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

def calc_average_age(column: pd.Series, year: int) -> float:
    dt = datetime(year, 12, 31) if year != 2023 else datetime(2023, 5, 7)
    age = column.apply(lambda x: (dt - x).total_seconds() / 86400 / 365.25)
    return age.mean() if isinstance(age.mean(), float) else 0


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Filter and compute the data and compute."""
    years = np.arange(1955, 2024)
    lst_length = []
    lst_power = []
    lst_avg_age = []
    for year in years:
        data_year = df.loc[
            (df["Kommerzieller Betrieb"] <= datetime(year, 12, 31)) &
            ((df["Abschaltung"] >= datetime(year, 12, 31)) | (df["Abschaltung"].isna()))]
        lst_power.append(data_year["Leistung, Netto in MW"].sum())
        lst_length.append(len(data_year))

        avg_age = calc_average_age(data_year["Kommerzieller Betrieb"], year)
        lst_avg_age.append(avg_age)

    d = pd.DataFrame()
    d["years"] = years
    d.set_index("years", inplace=True)
    d["num"] = lst_length
    d["power"] = lst_power
    d["avg_age"] = lst_avg_age

    return d


def plot_data(df: pd.DataFrame) -> None:
    """Plot the number of operating nuclear reactors and their capacity."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df.index,
        y=df["num"],
        name="Number of Operating Nuclear Reactors",
        marker=dict(color=df["avg_age"], showscale=True, coloraxis="coloraxis1"),
        hovertemplate="Number of Reactors: %{y}<br>Average Age of Reactors: %{marker.color:.2f} Years<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["power"] / 1000,
        name="Total Net Capacity",
        mode="lines+markers",
        marker=dict(color="black"),
        yaxis="y2",
        hovertemplate="Total Net Capacity: %{y:.2f} GW<extra></extra>",
    ))

    fig.update_layout(
        title="Evolution of Nuclear Power Plants in Europe:<br>Count, Total Net Capacity, and Average Age of Operating Nuclear Reactors",
        xaxis=dict(title=None,
                   showgrid=True, gridwidth=1, gridcolor="rgba(128, 128, 128, 0.1)"),
        yaxis=dict(title="Number of Operating Nuclear Reactors",
                   showgrid=True, gridwidth=1, gridcolor="rgba(128, 128, 128, 0.1)",
                   range=[-5, 210]),
        yaxis2=dict(title="Net Capacity in GW", overlaying="y",
                side="right", showgrid=False, range=[-5, 170]),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(family="sans-serif", color="black", size=12),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font=dict(size=12)),
        legend=dict(x=0.03, y=0.8,
                    xanchor="left", yanchor="bottom"),
        coloraxis1=dict(
        colorscale="Emrld",
        colorbar=dict(x=1, y=1.2, len=0.3, thickness=20, orientation="h",
                      xanchor="right", yanchor="top",
                      title="Average Age in Years", titleside="top")
    ),
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

    FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ee-nuclear-commissioning", "data", FILE_NAME))

    # Read and preprocess the data
    df = read_data(FILE_PATH)

    # Process the data
    data = process_data(df)

    # Plot the data
    plot_data(data)


if __name__ == "__main__":
    main()
