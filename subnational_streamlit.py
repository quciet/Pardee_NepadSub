import streamlit as st
import SessionState
# Pandas
import numpy as np
import pandas as pd
import copy
# mysql connector
from mysql.connector import MySQLConnection
import mysql.connector
# csv file
import base64
# 
from datetime import datetime

# Build Connection to nepadsub MySQL database
db_conn = MySQLConnection(
    user='xyt',
    passwd='Wsdbc!1992',
    database='NepadSub',
    host='127.0.0.1',
    allow_local_infile='1'
)
db_corsor = db_conn.cursor(buffered=True)

#--------------------------------------------------------------------------
# Data Query functions
# mapping from country to its subdivisions
@st.cache(hash_funcs={MySQLConnection: id})
def all_country_sub(db_conn):
    country_sub= pd.read_sql("SELECT DISTINCT Country, Subdivision FROM DataSeries;",\
     con=db_conn)
    return country_sub
# mapping from country to issue areas
@st.cache(hash_funcs={MySQLConnection: id})
def all_group_var(db_conn):
    group_var = pd.read_sql('SELECT Country, VarGroup, VarName FROM metadata;', con=db_conn)
    return group_var
# select data for specific country-subdivision-vars
@st.cache(hash_funcs={MySQLConnection: id})
def get_country_sub(country_list=[], subdivision_list=[], varname_list=[], db_conn=db_conn):
    #
    def add_q(q_list):
        q_str_list= ["'"+ i +"'" for i in q_list]
        q_str= ",".join(q_str_list)
        return q_str
    #
    select_string= "SELECT * FROM DataSeries"
    #
    if len(country_list) + len(subdivision_list) + len(varname_list) > 0:
        for l in ["country", "subdivision", "varname"]:
            if len(eval(l+"_list")) > 0:
                if " Where " not in select_string:
                    select_string+= f" Where {l} in ("+\
                     add_q(eval(l+"_list")) +")"
                else:
                    select_string+= f" AND {l} in ("+ add_q(eval(l+"_list")) +")"
        select_country_sub= pd.read_sql(select_string, con=db_conn)
    else:
        select_country_sub= pd.read_sql(select_string, con=db_conn)
    return select_country_sub, select_string
# metadata for


#--------------------------------------------------------------------------
# Webpage
# Title
st.title('NEPAD Sub-National Data Preview Tool')

# Image AUDA
st.image('img/African Union Development Agency-NEPAD logo_caps_EN.JPG',
        use_column_width=True) #, caption='NEPAD Sub-National DataPreview Tool'

# Load Selection Data
select_group_var = all_group_var(db_conn)
select_country_sub = all_country_sub(db_conn)

# Prepare a SessionState for user input:
ss_sideselect = SessionState.get(select_set=[], keeptable=False, result_table=None)

# Select box for countries
country_available = list(select_country_sub.Country.drop_duplicates())
opt_country = st.sidebar.multiselect(
    label= 'Select Countries',
    options= country_available)

# Select box for subdivision
sub_available = list(select_country_sub[select_country_sub.Country.\
isin(opt_country)].Subdivision)
opt_sub = st.sidebar.multiselect(
    label= 'Select Subdivisions',
    options= sub_available)

# Select box for issue area
group_available = list(select_group_var.VarGroup.drop_duplicates())
opt_group = st.sidebar.multiselect(
    label= 'Select Development Areas',
    options= group_available)

# Select box for var
if opt_group:
    var_available = list(select_group_var[select_group_var.VarGroup.\
    isin(opt_group)].VarName.drop_duplicates())
else:
    var_available = list(select_group_var.VarName.drop_duplicates())
opt_var = st.sidebar.multiselect(
    label= 'Select Data',
    options= var_available)

# Slider for year range
year_sl= st.sidebar.slider("Year Range", min_value=1960, max_value=2020, 
                           value=(1960, 2020), step=1)

# Load Selection
if st.sidebar.button('Add'):
    ss_sideselect.select_set.append([opt_country, opt_sub, opt_group, opt_var, year_sl])
    st.write(ss_sideselect.select_set)

if st.sidebar.button('Get Data'):
    result_dt, query = get_country_sub(country_list=opt_country,\
                    subdivision_list=opt_sub, varname_list=opt_var,\
                    db_conn=db_conn)
    if year_sl[0]>1960:
        for y in range(1960, year_sl[0]):
            try:
                result_dt.drop(columns=str(y), inplace=True)
            except:
                continue
    if year_sl[1]<2020:
        for y in range(1+year_sl[1], 2020):
            try:
                result_dt.drop(columns=str(y), inplace=True)
            except:
                continue
    result_dt.dropna(how="all", axis="columns", inplace=True)
    # st.write(query)
    ss_sideselect.keeptable=True
    ss_sideselect.result_table=result_dt
    #

if ss_sideselect.keeptable==True:
    result_dt=ss_sideselect.result_table
    st.dataframe(result_dt)
    ##
    csv_download= ss_sideselect.result_table.to_csv(index=False)
    b64= base64.b64encode(csv_download.encode()).decode()
    filename= datetime.now().strftime("%H:%M:%S")
    href_download= f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download CSV File</a>'
    st.markdown(href_download, unsafe_allow_html=True)

    #
if ss_sideselect.keeptable==True and st.checkbox('Show Line Chart'):
    if not ss_sideselect.result_table.empty:
        result_dt_line= result_dt.copy(deep=True)
        result_dt_line_cname=list(result_dt_line["FIPS_CODE"])
        result_dt_line.drop(columns=["Country","Subdivision",\
        "FIPS_CODE","VarName","Earliest","MostRecent"], inplace=True)
        result_dt_line= result_dt_line.transpose()
        result_dt_line.columns= result_dt_line_cname
        # st.dataframe(result_dt_line)
        st.line_chart(data=result_dt_line, \
        width=0, height=0, use_container_width=True)


