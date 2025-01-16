# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custome smoothie
    """
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be ", name_on_order)

cnx = st.connection('snowflake')
session = cnx.session() 
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'), col('search_on'))

# Convert to pandas to use LOC
pd_df = my_dataframe.to_pandas()


ingredients_list = st.multiselect(
    'Choose up to five ingredients for your smoothie'
    , my_dataframe
    , max_selections = 5
)

if ingredients_list:
    ingredients_string = ''
    for ingredients in ingredients_list:
        ingredients_string += ingredients + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == ingredients, 'SEARCH_ON'].iloc[0]

        st.subheader(ingredients + ' Nutrition information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values ('""" + ingredients_string + """','""" + name_on_order + """')"""
    
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

