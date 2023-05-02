iimport
pandas as pd
import plotly.express as px
import streamlit as st
import warnings
import pymysql
import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide")
# DATASETS
data_aggreation_transaction_df= pd.read_csv(r'/content/Phonepepulse/data_aggregation_transacation.csv')
data_aggregation_user_summ_df = pd.read_csv(r'/content/Phonepepulse/data_aggretation_user_sum_file.csv')
data_aggregation_user_df = pd.read_csv(r'/content/Phonepepulse/data_aggregation_user_file.csv')
geo_scatter_dataset_visualize = pd.read_csv(r'/content/Phonepepulse/data_map_dis_lat_lang_file.csv')
Map_states_dataset = pd.read_csv(r'/content/Phonepepulse/datamap_states.csv')
map_transaction_dataset = pd.read_csv(r'/content/Phonepepulse/datamap_transaction.csv')
data_map_user_table_df = pd.read_csv(r'/content/Phonepepulse/map_user_file.csv')
states_india_df = pd.read_csv(r'/content/Phonepepulse/state_latitude_langitude.csv')

colT1, colT2 = st.columns([1, 5])
with colT2:
    st.title('PhonePePulse Data Analysis')
c1, c2 = st.columns(2)
with c1:
    Year = st.selectbox(
        'Please select the Year',
        ('2018', '2019', '2020', '2021', '2022'))
with c2:
    Quarter = st.selectbox(
        'Please select the Quarter',
        ('1', '2', '3', '4'))
year = int(Year)
quarter = int(Quarter)
Trans_scatter = map_transaction_dataset.loc[
    (map_transaction_dataset['Year'] == year) & (map_transaction_dataset['Quarter'] == quarter)].copy()
Transaction_Coropleth_States = Trans_scatter[Trans_scatter["State"] == "india"]
Trans_scatter.drop(
    Trans_scatter.index[(Trans_scatter["State"] == "india")], axis=0, inplace=True)
# Dynamic Scattergeo Data Generation
Trans_scatter = Trans_scatter.sort_values(by=['Place_Name'], ascending=False)
geo_scatter_dataset_visualize = Trans_scatter.sort_values(by=['District'], ascending=False)
Total_Amount = []
for i in Trans_scatter['Total_Amount']:
    Total_Amount.append(i)
geo_scatter_dataset_visualize['Total_Amount'] = Total_Amount
Total_Transaction = []
for i in Trans_scatter['Total_Transactions_count']:
    Total_Transaction.append(i)
geo_scatter_dataset_visualize['Total_Transactions'] = Total_Transaction
geo_scatter_dataset_visualize['Year_Quarter'] = str(year) + '-Q' + str(quarter)
# Dynamic Coropleth
Map_states_dataset = Map_states_dataset.sort_values(by=['state'], ascending=False)
Transaction_Coropleth_States = Transaction_Coropleth_States.sort_values(by=['Place_Name'], ascending=False)
Total_Amount = []
for i in Transaction_Coropleth_States['Total_Amount']:
    Total_Amount.append(i)
Map_states_dataset['Total_Amount'] = Total_Amount
Total_Transaction = []
for i in Transaction_Coropleth_States['Total_Transactions_count']:
    Total_Transaction.append(i)
Map_states_dataset['Total_Transactions'] = Total_Transaction
# -------------------------------------FIGURE1 INDIA MAP------------------------------------------------------------------
# scatter plotting the states codes
states_india_df = Map_states_dataset.sort_values(by=['state'], ascending=False)
states_india_df['Registered_Users'] = Map_states_dataset['Registered_Users']
states_india_df['Total_Amount'] = Map_states_dataset['Total_Amount']
states_india_df['Total_Transactions'] = Map_states_dataset['Total_Transactions']
states_india_df['Year_Quarter'] = str(year) + '-Q' + str(quarter)
fig = px.scatter_geo(states_india_df,
                     lon=states_india_df['Longitude'],
                     lat=states_india_df['Latitude'],
                     text=states_india_df['code'],  # It will display district names on map
                     hover_name="state",
                     hover_data=['Total_Amount', "Total_Transactions", "Year_Quarter"],
                     )
fig.update_traces(marker=dict(color="white", size=0.3))
fig.update_geos(fitbounds="locations", visible=False, )
# scatter plotting districts
geo_scatter_dataset_visualize['col'] = geo_scatter_dataset_visualize['Total_Transactions']
fig1 = px.scatter_geo(geo_scatter_dataset_visualize,
                      lon=geo_scatter_dataset_visualize['Longitude'],
                      lat=geo_scatter_dataset_visualize['Latitude'],
                      color=geo_scatter_dataset_visualize['col'],
                      size=geo_scatter_dataset_visualize['Total_Transactions'],
                      text = geo_scatter_dataset_visualize['District'],
                      hover_name="District",
                      hover_data=["State", "Total_Amount", "Total_Transactions", "Year_Quarter"],
                      title='District',
                      size_max=22, )
fig1.update_traces(marker=dict(color="rebeccapurple", line_width=1))
# coropleth mapping india
fig_ch = px.choropleth(
    Map_states_dataset,
    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
    featureidkey='properties.ST_NM',
    locations='state',
    color="Total_Transactions",
)
fig_ch.update_geos(fitbounds="locations", visible=False, )
# combining districts states and coropleth
fig_ch.add_trace(fig.data[0])
fig_ch.add_trace(fig1.data[0])
st.write("### **:blue[PhonePe India Map]**")
colT1, colT2 = st.columns([6, 4])
with colT1:
    st.plotly_chart(fig_ch, use_container_width=True)
with colT2:
    st.info()
    st.info()
# -----------------------------------------------FIGURE2 HIDDEN BARGRAPH------------------------------------------------------------------------
Map_states_dataset = Map_states_dataset.sort_values(by=['Total_Transactions'])
fig = px.bar(Map_states_dataset, x='state', y='Total_Transactions', title=str(year) + " Quarter-" + str(quarter))
with st.expander("See Bar graph for the same data"):
    st.plotly_chart(fig, use_container_width=True)
    st.info(
        '**:blue[The above bar graph showing the increasing order of PhonePe Transactions according to the states of India, Here we can observe the top states with highest Transaction by looking at graph]**')

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ TRANSACTIONS ANALYSIS @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

st.write('# :green[TRANSACTIONS ANALYSIS :currency_exchange:]')
tab1, tab2, tab3, tab4 = st.tabs(["STATE ANALYSIS", "DISTRICT ANALYSIS", "YEAR ANALYSIS", "OVERALL ANALYSIS"])
# ==================================================T FIGURE1 STATE ANALYSIS=======================================================
with tab1:
    Data_Aggregated_Transaction = data_aggreation_transaction_df.copy()
    Data_Aggregated_Transaction.drop(
        Data_Aggregated_Transaction.index[(Data_Aggregated_Transaction["State"] == "india")], axis=0, inplace=True)
    State_PaymentMode = Data_Aggregated_Transaction.copy()
    # st.write('### :green[State & PaymentMode]')
    col1, col2 = st.columns(2)
    with col1:
        mode = st.selectbox(
            'Please select the Mode',
            ('Recharge & bill payments', 'Peer-to-peer payments', 'Merchant payments', 'Financial Services', 'Others'),
            key='a')
    with col2:
        state = st.selectbox(
            'Please select the State',
            ('andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh',
             'assam', 'bihar', 'chandigarh', 'chhattisgarh',
             'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat',
             'haryana', 'himachal-pradesh', 'jammu-&-kashmir',
             'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep',
             'madhya-pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram',
             'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan',
             'sikkim', 'tamil-nadu', 'telangana', 'tripura', 'uttar-pradesh',
             'uttarakhand', 'west-bengal'), key='b')
    State = state
    Year_List = [2018, 2019, 2020, 2021, 2022]
    Mode = mode
    State_PaymentMode = State_PaymentMode.loc[
        (State_PaymentMode['State'] == State) & (State_PaymentMode['Year'].isin(Year_List)) &
        (State_PaymentMode['Payment_Mode'] == Mode)]
    State_PaymentMode = State_PaymentMode.sort_values(by=['Year'])
    State_PaymentMode["Quarter"] = "Q" + State_PaymentMode['Quarter'].astype(str)
    State_PaymentMode["Year_Quarter"] = State_PaymentMode['Year'].astype(str) + "-" + State_PaymentMode[
        "Quarter"].astype(str)
    fig = px.bar(State_PaymentMode, x='Year_Quarter', y='Total_Transactions_count', color="Total_Transactions_count",
                 color_continuous_scale="Viridis")

    colT1, colT2 = st.columns([7, 3])
    with colT1:
        st.write('#### ' + State.upper())
        st.plotly_chart(fig, use_container_width=True)
    with colT2:
        st.info()
        st.info()
# =============================================T FIGURE2 DISTRICTS ANALYSIS=============================================
with tab2:
    col1, col2, col3 = st.columns(3)
    with col1:
        Year = st.selectbox(
            'Please select the Year',
            ('2018', '2019', '2020', '2021', '2022'), key='y1')
    with col2:
        state = st.selectbox(
            'Please select the State',
            ('andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh',
             'assam', 'bihar', 'chandigarh', 'chhattisgarh',
             'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat',
             'haryana', 'himachal-pradesh', 'jammu-&-kashmir',
             'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep',
             'madhya-pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram',
             'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan',
             'sikkim', 'tamil-nadu', 'telangana', 'tripura', 'uttar-pradesh',
             'uttarakhand', 'west-bengal'), key='dk')
    with col3:
        Quarter = st.selectbox(
            'Please select the Quarter',
            ('1', '2', '3', '4'), key='qwe')
    districts = map_transaction_dataset.loc[
        (map_transaction_dataset ['State'] == state) & (map_transaction_dataset['Year'] == int(Year))
        & (map_transaction_dataset['Quarter'] == int(Quarter))]
    l = len(districts)
    fig = px.bar(districts, x='Place_Name', y='Total_Transactions_count', color="Total_Transactions_count",
                 color_continuous_scale="Viridis")
    colT1, colT2 = st.columns([7, 3])
    with colT1:
        st.write('#### ' + state.upper() + ' WITH ' + str(l) + ' DISTRICTS')
        st.plotly_chart(fig, use_container_width=True)
    with colT2:
        st.info()
        st.info()
# =============================================T FIGURE3 YEAR ANALYSIS===================================================
with tab3:
    col1, col2 = st.columns(2)
    with col1:
        M = st.selectbox(
            'Please select the Mode',
            ('Recharge & bill payments', 'Peer-to-peer payments', 'Merchant payments', 'Financial Services', 'Others'),
            key='D')
    with col2:
        Y = st.selectbox(
            'Please select the Year',
            ('2018', '2019', '2020', '2021', '2022'), key='F')
    Year_PaymentMode = Data_Aggregated_Transaction.copy()
    Year = int(Y)
    Mode = M
    Year_PaymentMode = Year_PaymentMode.loc[(Year_PaymentMode['Year'] == Year) &
                                            (Year_PaymentMode['Payment_Mode'] == Mode)]
    States_List = Year_PaymentMode['State'].unique()
    State_groupby_YP = Year_PaymentMode.groupby('State')
    Year_PaymentMode_Table = State_groupby_YP.sum()
    Year_PaymentMode_Table['states'] = States_List
    del Year_PaymentMode_Table['Quarter']  # ylgnbu', 'ylorbr', 'ylorrd teal
    del Year_PaymentMode_Table['Year']
    Year_PaymentMode_Table = Year_PaymentMode_Table.sort_values(by=['Total_Transactions_count'])
    fig2 = px.bar(Year_PaymentMode_Table, x='states', y='Total_Transactions_count', color="Total_Transactions_count",
                  color_continuous_scale="Viridis", )
    colT1, colT2 = st.columns([7, 3])
    with colT1:
        st.write('#### ' + str(Year) + ' DATA ANALYSIS')
        st.plotly_chart(fig2, use_container_width=True)
    with colT2:
        st.info()
        st.info()
# =============================================T FIGURE4 OVERALL ANALYSIS=============================================
with tab4:
    years = Data_Aggregated_Transaction.groupby('Year')
    years_List = Data_Aggregated_Transaction['Year'].unique()
    years_Table = years.sum()
    del years_Table['Quarter']
    years_Table['year'] = years_List
    total_trans = years_Table['Total_Transactions_count'].sum()  # this data is used in sidebar
    fig1 = px.pie(years_Table, values='Total_Transactions_count', names='year',
                  color_discrete_sequence=px.colors.sequential.Viridis, title='TOTAL TRANSACTIONS (2018 TO 2022)')
    col1, col2 = st.columns([0.65, 0.35])
    with col1:
        st.write('### :green[Drastical Increase in Transactions :rocket:]')
        st.plotly_chart(fig1)
    with col2:
        st.write('#### :green[Year Wise Transaction Analysis in INDIA]')
        st.markdown(years_Table.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.info(


        )

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ USER ANALYSIS @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

st.write('# :orange[USERS DATA ANALYSIS ]')
tab1, tab2, tab3, tab4 = st.tabs(["STATE ANALYSIS", "DISTRICT ANALYSIS", "YEAR ANALYSIS", "OVERALL ANALYSIS"])

# =================================================U STATE ANALYSIS ========================================================
with tab1:
    st.write('### :blue[State & Userbase]')
    state = st.selectbox(
        'Please select the State',
        ('andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh',
         'assam', 'bihar', 'chandigarh', 'chhattisgarh',
         'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat',
         'haryana', 'himachal-pradesh', 'jammu-&-kashmir',
         'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep',
         'madhya-pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram',
         'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan',
         'sikkim', 'tamil-nadu', 'telangana', 'tripura', 'uttar-pradesh',
         'uttarakhand', 'west-bengal'), key='W')
    app_opening = data_aggregation_user_summ_df.groupby(['State', 'Year'])
    a_state = app_opening.sum()
    la = data_aggregation_user_summ_df['State'] + "-" + data_aggregation_user_summ_df["Year"].astype(str)
    a_state["state_year"] = la.unique()
    sta = a_state["state_year"].str[:-5]
    a_state["state"] = sta
    sout = a_state.loc[(a_state['state'] == state)]
    ta = sout['AppOpenings'].sum()
    tr = sout['Registered_Users'].sum()
    sout['AppOpenings'] = sout['AppOpenings'].mul(100 / ta)
    sout['Registered_Users'] = sout['Registered_Users'].mul(100 / tr).copy()
    fig = go.Figure(data=[
        go.Bar(name='AppOpenings %', y=sout['AppOpenings'], x=sout['state_year'], marker={'color': 'pink'}),
        go.Bar(name='Registered Users %', y=sout['Registered_Users'], x=sout['state_year'], marker={'color': 'orange'})
    ])
    # Change the bar mode
    fig.update_layout(barmode='group')
    colT1, colT2 = st.columns([7, 3])
    with colT1:
        st.write("#### ", state.upper())
        st.plotly_chart(fig, use_container_width=True, height=200)
    with colT2:
        st.info()
        st.info()
# ==================================================U DISTRICT ANALYSIS ====================================================
with tab2:
    col1, col2, col3 = st.columns(3)
    with col1:
        Year = st.selectbox(
            'Please select the Year',
            ('2022', '2021', '2020', '2019', '2018'), key='y12')
    with col2:
        state = st.selectbox(
            'Please select the State',
            ('andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh',
             'assam', 'bihar', 'chandigarh', 'chhattisgarh',
             'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat',
             'haryana', 'himachal-pradesh', 'jammu-&-kashmir',
             'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep',
             'madhya-pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram',
             'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan',
             'sikkim', 'tamil-nadu', 'telangana', 'tripura', 'uttar-pradesh',
             'uttarakhand', 'west-bengal'), key='dk2')
    with col3:
        Quarter = st.selectbox(
            'Please select the Quarter',
            ('1', '2', '3', '4'), key='qwe2')
    districts = data_map_user_table_df .loc[
        (data_map_user_table_df ['State'] == state) & (data_map_user_table_df ['Year'] == int(Year))
        & (data_map_user_table_df ['Quarter'] == int(Quarter))]
    l = len(districts)
    fig = px.bar(districts, x='Place_Name', y='App_Openings', color="App_Openings",
                 color_continuous_scale="reds")
    colT1, colT2 = st.columns([7, 3])
    with colT1:
        if l:
            st.write('#### ' + state.upper() + ' WITH ' + str(l) + ' DISTRICTS')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write('#### NO DISTRICTS DATA AVAILABLE FOR ' + state.upper())

    with colT2:
        if l:
            st.info()
            st.info()
with tab3:
    st.write('### :orange[Brand Share] ')
    col1, col2 = st.columns(2)
    with col1:
        state = st.selectbox(
            'Please select the State',
            ('india', 'andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh',
             'assam', 'bihar', 'chandigarh', 'chhattisgarh',
             'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat',
             'haryana', 'himachal-pradesh', 'jammu-&-kashmir',
             'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep',
             'madhya-pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram',
             'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan',
             'sikkim', 'tamil-nadu', 'telangana', 'tripura', 'uttar-pradesh',
             'uttarakhand', 'west-bengal'), key='Z')
    with col2:
        Y = st.selectbox(
            'Please select the Year',
            ('2018', '2019', '2020', '2021', '2022'), key='X')
    y = int(Y)
    s = state
    brand = data_aggregation_user_df [data_aggregation_user_df['Year'] == y]
    brand = data_aggregation_user_df .loc[
        (data_aggregation_user_df ['Year'] == y) & (data_aggregation_user_df ['State'] == s)]
    myb = brand['Brand_Name'].unique()
    x = sorted(myb).copy()
    b = brand.groupby('Brand_Name').sum()
    b['brand'] = x
    br = b['Registered_Users_Count'].sum()
    labels = b['brand']
    values = b['Registered_Users_Count']  # customdata=labels,
    fig3 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, textinfo='label+percent',
                                  texttemplate='%{label}<br>%{percent:1%f}', insidetextorientation='horizontal',
                                  textfont=dict(color='#000000'), marker_colors=px.colors.qualitative.Prism)])

    colT1, colT2 = st.columns([7, 3])
    with colT1:
        st.write("#### ", state.upper() + ' IN ' + Y)
        st.plotly_chart(fig3, use_container_width=True)
    with colT2:
        st.info()
        st.info()
    b = b.sort_values(by=['Registered_Users_Count'])
    fig4 = px.bar(b, x='brand', y='Registered_Users_Count', color="Registered_Users_Count",
                  title='In ' + state + 'in ' + str(y),
                  color_continuous_scale="oranges", )
    with st.expander("See Bar graph for the same data"):
        st.plotly_chart(fig4, use_container_width=True)
    # ===================================================U OVERALL ANALYSIS ====================================================

    with tab4:
        years = data_aggregation_user_summ_df.groupby('Year')
        years_List = data_aggregation_user_summ_df['Year'].unique()
        years_Table = years.sum()
        del years_Table['Quarter']
        years_Table['year'] = years_List
        total_trans = years_Table['Registered_Users'].sum()  # this data is used in sidebar
        fig1 = px.pie(years_Table, values='Registered_Users', names='year',
                      color_discrete_sequence=px.colors.sequential.RdBu, title='TOTAL REGISTERED USERS (2018 TO 2022)')
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            # st.write('### :green[Drastical Increase in Transactions :rocket:]')
            labels = ["US", "China", "European Union", "Russian Federation", "Brazil", "India",
                      "Rest of World"]

            # Create subplots: use 'domain' type for Pie subplot
            fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]])
            fig.add_trace(
                go.Pie(labels=years_Table['year'], values=years_Table['Registered_Users'], name="REGISTERED USERS"),
                1, 1)
            fig.add_trace(go.Pie(labels=years_Table['year'], values=years_Table['AppOpenings'], name="APP OPENINGS"),
                          1, 2)

            # Use `hole` to create a donut-like pie chart
            fig.update_traces(hole=.6, hoverinfo="label+percent+name")

            fig.update_layout(
                title_text="USERS DATA (2018 TO 2022)",
                # Add annotations in the center of the donut pies.
                annotations=[dict(text='USERS', x=0.18, y=0.5, font_size=20, showarrow=False),
                             dict(text='APP', x=0.82, y=0.5, font_size=20, showarrow=False)])
            # st.plotly_chart(fig1)
            st.plotly_chart(fig)
        with col2:
            # st.write('#### :green[Year Wise Transaction Analysis in INDIA]')
            st.markdown(years_Table.style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.info()
    
    st.write('# :green[TOP 3 STATES]')
    c1, c2 = st.columns(2)
    with c1:
        Year = st.selectbox(
            'Please select the Year',
            ('2022', '2021', '2020', '2019', '2018'), key='y1h2k')
    with c2:
        Quarter = st.selectbox(
            'Please select the Quarter',
            ('1', '2', '3', '4'), key='qgwe2')
    Data_Map_User_df = data_aggregation_user_summ_df.copy()
    top_states = Data_Map_User_df.loc[
        (Data_Map_User_df['Year'] == int(Year)) & (Data_Map_User_df['Quarter'] == int(Quarter))]
    top_states_r = top_states.sort_values(by=['Registered_Users'], ascending=False)
    top_states_a = top_states.sort_values(by=['AppOpenings'], ascending=False)
    
    top_states_T = data_aggreation_transaction_df.loc[
        (data_aggreation_transaction_df['Year'] == int(Year)) & (data_aggreation_transaction_df['Quarter'] == int(Quarter))]
    topst = top_states_T.groupby('State')
    x = topst.sum().sort_values(by=['Total_Transactions_count'], ascending=False)
    y = topst.sum().sort_values(by=['Total_Amount'], ascending=False)
    col1, col2, col3, col4 = st.columns([2.5, 2.5, 2.5, 2.5])
    with col1:
        rt = top_states_r[1:4]
        st.markdown("#### :orange[Registered Users :bust_in_silhouette:]")
        st.markdown(rt[['State', 'Registered_Users']].style.hide(axis="index").to_html(), unsafe_allow_html=True)
    with col2:
        at = top_states_a[1:4]
        st.markdown("#### :orange[PhonePeApp Openings:iphone:]")
        st.markdown(at[['State', 'AppOpenings']].style.hide(axis="index").to_html(), unsafe_allow_html=True)
    with col3:
        st.markdown("#### :orange[Total Transactions:currency_exchange:]")
        st.write(x[['Total_Transactions_count']][1:4])
    with col4:
        st.markdown("#### :orange[Total Amount :dollar:]")
        st.write(y['Total_Amount'][1:4])