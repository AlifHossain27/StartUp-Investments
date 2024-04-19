import pycountry
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.subplots as sp
import plotly.graph_objects as go

# Page Configs
st.set_page_config(page_title="StartUp Investments", page_icon="📊", layout='wide', initial_sidebar_state='expanded')

# CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Convert String to Integer
def str_to_int(s: str):
    try:
        s = s.replace(',', '')
        if '-' in s:
            s = 0
        return int(s)
    except ValueError:
        return s
    except AttributeError:
        return s

# Convert Float to String
def float_to_str(f: int):
    try:
        f = int(f)
        return str(f)
    except ValueError:
        return f
    except AttributeError:
        return f

# Convert Country code to Country name   
def code_to_country(text: str):
    if text == 'ROM':
        text = 'ROU'
    return pycountry.countries.get(alpha_3=text).name

# Load data
@st.cache_data
def load_data(csv:str):
    df = pd.read_csv(csv, encoding= 'unicode_escape')
    return df

# Preproccessing the Dataframe
@st.cache_data
def pre_process(df):
    df = df.rename({' funding_total_usd ': 'funding_total_usd', ' market ': 'market'}, axis='columns')
    df = df.drop('state_code', axis=1)
    df = df.drop(['permalink', 'homepage_url', 'category_list'], axis=1)
    df['funding_total_usd'] = df['funding_total_usd'].apply(str_to_int)
    df['founded_year'] = df['founded_year'].apply(float_to_str)
    df = df[df['funding_total_usd']!=0]
    df = df.dropna()
    df = df.drop_duplicates()
    df['country'] = df['country_code'].apply(code_to_country)
    df.drop('country_code', axis=1, inplace=True)
    return df

# Data Table View
def data_table(data):
    with st.expander("VIEW EXCEL DATASET"):
        showData=st.multiselect(label='Filter: ', options=data.columns, default=['name', 'market', 'funding_total_usd', 'status', 'city', 'founded_at', 'first_funding_at', 'last_funding_at'])
        st.dataframe(data[showData],use_container_width=True)

# Total investments
@st.cache_data
def total_investments(data):
    investment_data = data[["round_A","round_B","round_C","round_D","round_E","round_F","round_G","round_H"]].sum()
    new_data = pd.DataFrame({
        "rounds": investment_data.index,
        "value": investment_data.values
    })
    return round(new_data['value'].sum())

# Total Fundings
@st.cache_data
def total_fundings(data):
    funding_data = data["funding_total_usd"].sum()
    return round(funding_data)

# Total Companies Invested in
@st.cache_data
def total_companies_invested(data):
    invested_companies = data['name'].nunique()
    return invested_companies

# Pie Chart to show most expensive market
@st.cache_data
def expensive_markets_pie_chart(data, slider):
    top_spheres = data['market'].value_counts()[:slider]
    fig = px.pie(values=top_spheres, names=top_spheres.index, title=f'Top {slider} most expensive markets')
    return fig

# Histogram to show StartUp Status
@st.cache_data
def startup_status_histogram(data, select):
    filtered_data = data[data["status"].isin(select)]
    fig = px.histogram(filtered_data["status"], title='Startups status')
    fig.update_xaxes(categoryorder='total ascending')
    fig.update_layout(yaxis_title='Count')
    fig.update_layout(xaxis_title='Status')
    return fig

# Histogram to show Investments in round
@st.cache_data
def rounds_histogram(data, select):
    filtered_data = data[select].sum()
    new_data = pd.DataFrame({
        "rounds": filtered_data.index,
        "investments": filtered_data.values
    })
    fig = px.histogram(new_data,x='rounds', y='investments', title='Investments in Round', color_discrete_sequence=["mediumpurple"])
    fig.update_layout(yaxis_title='Investments')
    fig.update_layout(xaxis_title='Rounds')
    return fig

# Line chart to show Funding required each year
@st.cache_data
def funding_line_chart(data):
    years = set(data['founded_year'])
    fund_by_year = {}
    for year in sorted(years):
        fund_by_year[year] = data[data['founded_year']==year]['funding_total_usd'].sum()/10**9
    fig = px.line(x = fund_by_year.keys(), y=fund_by_year.values(), labels={'x': 'Year', 'y': 'Funding in $ billions'}, color_discrete_sequence=["darkorange"], title="Funding required each year")
    return fig

# Scatter to show Correlation between debt financing and startup funding
@st.cache_data
def debt_funding_scatter_plot(data):
    fig = px.scatter(
        data[(data['debt_financing']>0)&(data['funding_total_usd']/10**9 < 30)],
        x='funding_total_usd',
        y='debt_financing',
        trendline="ols",
        title='Correlation between debt financing and startup funding'
    )
    fig.update_layout(yaxis_title='Debt Financing')
    fig.update_layout(xaxis_title='Total Funding in USD')
    return fig

if __name__ == "__main__":
    # Getting the data
    data = pre_process(df=load_data(csv="investments_VC.csv"))

    # Side Bar
    st.sidebar.markdown('''
    # Configurations
    ---
    ''')
    st.sidebar.subheader("Top Markets")
    expensive_market_slider = st.sidebar.slider("Number of Markets: ", 2, 30, 5)
    st.sidebar.subheader("Investment Rounds")
    rounds_select = st.sidebar.multiselect(label="Filter by: ", options=["round_A","round_B","round_C","round_D","round_E","round_F","round_G","round_H"], default=["round_A","round_B","round_C","round_D","round_E","round_F","round_G","round_H"])
    st.sidebar.subheader("StartUp Status")
    status_select = st.sidebar.multiselect(label="Filter by: ", options=data["status"].unique(), default=["acquired", "operating"])
    st.sidebar.markdown('''
    ---
    Created by [Alif Hossain Sajib](https://github.com/AlifHossain27)
    ''')

    # Main Page
    st.markdown("## StartUp Investment Dashboard")
    data_table(data=data)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Invested Companies", total_companies_invested(data))
    col2.metric("Total Investment", f'$ {total_investments(data)}')
    col3.metric("Total Funding", f'$ {total_fundings(data)}')
    col4, col5 = st.columns((4,7))
    with col4:
        st.plotly_chart(expensive_markets_pie_chart(data=data, slider=expensive_market_slider), use_container_width=True)
    with col5:
        st.plotly_chart(rounds_histogram(data=data, select=rounds_select), use_container_width=True)
    col6, col7 = st.columns((7,4))
    with col6:
        st.plotly_chart(funding_line_chart(data=data), use_container_width=True)
    with col7:
        st.plotly_chart(startup_status_histogram(data=data, select=status_select), use_container_width=True)
    st.plotly_chart(debt_funding_scatter_plot(data=data), use_container_width=True)
    