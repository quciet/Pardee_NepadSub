# Select box for var
if option_group:
    var_available = select_group_var[select_group_var.VarGroup.\
    isin(option_group)].VarName.drop_duplicates().copy(deep=True)
else:
    var_available = select_group_var.VarName.drop_duplicates().copy(deep=True)
option_var = st.sidebar.multiselect(
    label= 'Select Data',
    options= var_available)
# Final Checkbox to show data
# get_country_sub(country_list= option_country, )



# Prepare a SessionState for user input:
ss_sideselect = SessionState.get(opt_c= set(), opt_s= set(), \
                                opt_g= set(), opt_v= set())


# Check box for all meta data
if st.checkbox('Show MetaData'):
    metadata= pd.read_sql('SELECT * FROM metadata', con=db_conn)
    metadata= metadata[["Country", "VarGroup", "VarName", "Definition",\
    "Units", "Years", "Source"]]
    st.dataframe(metadata)
