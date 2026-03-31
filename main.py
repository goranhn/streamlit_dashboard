from fileinput import filename

import streamlit as st
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime as dt


df = pd.read_excel("Adidas.xlsx")
st.set_page_config(layout="wide")
st.markdown("<style>div.block-container{padding-top: 1rem}</style>", unsafe_allow_html=True)
image_temp = Image.open("adidas.png")
image = image_temp.resize((150, 150))

col1, col2 = st.columns([0.1, 0.8])
with col1:
    st.markdown(
        """
        <style>
        .st-emotion-lmm3ws { /* This class name may change over versions */
            width: 200px;
            height: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.image(image)

html_title = """
<style>
    .title-test {
        font-weight: bold;
        padding: 5px;
        border-radius: 5px;
    }
</style>>
<center><h1 class="title-text">Adidas Sales Dashboard US</h1></center>
"""

with col2:
    st.markdown(html_title, unsafe_allow_html=True)

col3, col4, col5 = st.columns([0.07, 0.30, 0.3])

with col3:
    box_date = dt.datetime.now().strftime("%d/%b/%y")

    # Wrap everything in one centered div
    content = f"""
    <div style='text-align: center;'>
        <p>Last Updated by:</p>
        <p><strong>{box_date}</strong></p>
    </div>
    """

    st.markdown(content, unsafe_allow_html=True)

with col4:
    fig = px.bar(df, x="Retailer", y="TotalSales", color="Retailer",
                 labels={"TotalSales": "Total Sales {$}"},
                 title= "Total Sales by retailer", hover_data=["TotalSales"],
                 template="gridon", height=500)
    st.plotly_chart(fig, use_container_width=True)

df["Month_Year"] = df["InvoiceDate"].dt.strftime("%b ' %Y")
result = df.groupby(df["Month_Year"])["TotalSales"].sum().reset_index()

# 1. Convert the column to actual dates (so Python understands the order)
result['Month_Year'] = pd.to_datetime(result['Month_Year'])

# 2. Sort the data from oldest to newest
result = result.sort_values('Month_Year')

with col5:
    fig1 = px.line(result, x="Month_Year", y="TotalSales",
                   title="Total Sales Over Time", template="plotly_dark",
                   line_shape="spline",
                   color_discrete_sequence=["#00FFCC"])
    st.plotly_chart(fig1, use_container_width=True)

_, view1, dwn1, view2, dwn2 = st.columns([0.15, 0.20, 0.20, 0.20, 0.20])

with view1:
    expander = st.expander("Retailer wise Sales")
    data = df[["Retailer", "TotalSales"]].groupby(by="Retailer")["TotalSales"].sum()
    expander.write(data)

with dwn1:
    st.download_button("Download Data", data=data.to_csv().encode("utf-8"),
        file_name="RetailerSales.csv", mime="text/csv")

with view2:
    expander = st.expander("Monthly Sales")
    data = result
    expander.write(data)

with dwn2:
    st.download_button("Download Data", data=result.to_csv().encode("utf-8"),
                       file_name="Monthly Sales.csv", mime="text/csv")

st.divider()

result1 = df.groupby(by="State")[["TotalSales","UnitsSold"]].sum().reset_index()
result1 = result1.sort_values(by="TotalSales", ascending=False)

fig3 = go.Figure()
fig3.add_trace(go.Bar(x = result1["State"], y = result1["TotalSales"],
                      marker_color='#00CC96', name="Total Sales"))
fig3.add_trace(go.Scatter(x = result1["State"], y = result1["UnitsSold"], mode="lines",
                          line=dict(shape='spline', smoothing=1.3, width=3, color='#FF8C00'),
                          name="Units Sold", yaxis="y2"))

fig3.update_layout(
    title="State Performance: Sales Volume vs. Revenue",
    xaxis = dict(title = "State", tickangle=-45),
    yaxis = dict(title = "Total Sales ($)", showgrid=False),
    yaxis2 = dict(title = "Units Sold", overlaying="y", side="right"),
    template="plotly_dark",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=20, r=20, t=60, b=20)
)

_, col6 = st.columns([0.1,1])

with col6:
    st.plotly_chart(fig3, use_container_width=True)

_, view3, dwn3 = st.columns([0.5,0.45,0.45])

with view3:
    expander = st.expander("View Data for Sales by Units Sold")
    expander.write(result1)

with dwn3:
    st.download_button("Download Data", data=result1.to_csv().encode("utf-8"),
                       file_name="Sales_y_UnitsSold.csv", mime="text/csv")

st.divider()

_, col7 = st.columns([0.1,1])

treemap = df[["Region", "City", "TotalSales"]].groupby(by = ["Region", "City"])["TotalSales"].sum().reset_index()

def format_sales(value):
    return f"${value / 1_000_000:.2f}M"

treemap["TotalSales (formatted)"] = treemap["TotalSales"].apply(format_sales)

#Treemap
# fig4 = px.treemap(treemap, path=["Region", "City"],
#                   values="TotalSales",
#                   hover_name="TotalSales (formatted)",
#                   hover_data=["TotalSales (formatted)"],
#                   color="City", height=700, width=600)
# fig4.update_traces(textinfo="label+value")

#The Sunburst Chart
# fig4 = px.sunburst(
#     treemap,
#     path=["Region", "City"],
#     values="TotalSales",
#     color="Region", # Color by Region for better grouping
#     template="plotly_dark"
# )

#Horizontal Grouped Bar Chart
fig4 = px.bar(
    treemap.sort_values("TotalSales", ascending=False).head(20),
    x="TotalSales",
    y="City",
    color="Region",
    orientation='h',
    template="plotly_dark",
    title="Top Cities by Sales"
)

with col7:
    st.subheader(":point_right: Horizontal Grouped Bar Chart :chart_with_upwards_trend:")
    st.plotly_chart(fig4, use_container_width=True)
st.markdown("<h5 style='text-align: center;'>New York is our flagship city, but the West region provides our most consistent and broad-based sales volume\n</h5>", unsafe_allow_html=True)
st.markdown("")
st.markdown("")
_, view4, dwn4 = st.columns([0.35,0.45,0.45])

with view4:
    result2 = df[["Region", "City", "TotalSales"]].groupby(by=["Region","City"])["TotalSales"].sum()
    expander = st.expander("View Data for Sales by Region and City")
    expander.write(result2)

with dwn4:
    st.download_button("Download Data", data=result1.to_csv().encode("utf-8"),
                       file_name="Sales_by_Region.csv", mime="text/csv")

st.divider()
st.markdown("")
st.markdown("<h5 style='text-align: center;'>This is only for the purpose of hands-on creating dashboard with Streamlit framework.</h5>", unsafe_allow_html=True)
st.markdown("")
st.markdown("<p style='text-align: center;'>Created by: Goran Najm</p>", unsafe_allow_html=True)
