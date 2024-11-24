import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time


def replace_year(dt):
    if dt.year == 1900:
        return dt.replace(year=2024)
    else:
        return dt


# Streamlit app
st.title("Interactive heatmaps")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    with st.spinner("Processing data....."):
        data = pd.read_excel(uploaded_file)
        data['Date'] = data['Date'].ffill().astype(str)
        data['Time'] = data['Time'].astype(str)
        data['Datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], format="%a, %d/%b %H:%M:%S")
        data['Datetime'] = data['Datetime'].apply(replace_year)
        data = data.set_index('Datetime')
        time.sleep(1)
    st.write("Displaying first four rows of the file:")
    st.dataframe(data.head(4))
    column_options = ['Temperature', 'Humidity']
    selected_column = st.selectbox("Select a parameter", column_options,index = None)

    if selected_column:
        pivot_data = data.pivot_table(values=selected_column, index=data.index.hour, columns=data.index.date, aggfunc='first')
        x_max = pivot_data.columns.max()
        min_temp = pivot_data.min().min()
        max_temp = pivot_data.max().max()
        threshold_value = st.number_input(f"Enter the threshold {selected_column.lower()}")
        hovertemplate_str = f"Date: %{{x}}<br>Hour: %{{y}}<br>{selected_column}: %{{z}}<extra></extra>"
        try:
            if threshold_value:
                threshold_scale = (threshold_value-min_temp)/(max_temp-min_temp)

                fig = go.Figure(
                    data=go.Heatmap(
                        z=pivot_data.values,
                        x=pivot_data.columns,
                        y=pivot_data.index,
                        colorscale=[
                            [0.0, "white"],
                            [threshold_scale, "white"],
                            [threshold_scale, "red"],
                            [1.0, "red"]
                        ],
                        hovertemplate= hovertemplate_str,
                        colorbar=dict(
                            title=selected_column,
                            tickvals=[min_temp, threshold_value, max_temp],
                            ticktext=[f"Min {selected_column} = {min_temp}", f"Threshold {selected_column} = {threshold_value}", f"Max {selected_column} = {max_temp}"],
                            outlinecolor='black',
                            outlinewidth=2,
                            tickcolor='black',
                        ),
                        xgap = 1,
                        ygap = 1,
                        zmin=min_temp,
                        zmax=max_temp,
                        showscale=True,
                    ),
                )
                fig.update_layout(
                    title = dict(
                        text = f"Yearly {selected_column} Heatmap",
                            x = 0.5,
                            xanchor = "center",
                            xref = 'container',
                        ),
                        xaxis=dict(
                                    range=[pivot_data.columns.min(), x_max],
                                    tickformat='%b',
                                    dtick = 'M1',
                                    title = "Date (Year 2024)",
                                    ),
                    yaxis = dict(range = [0,24],dtick = 4, title = "Hours"),         
                )
                st.plotly_chart(fig)
        except ValueError:
            st.write("Invalid input")