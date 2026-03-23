# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests  

# Write directly to the app
st.title(":apple: Customize Your Smoothie! :strawberry:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Smoothie name:")
st.write("The name of the Smoothie is:", name_on_order)

# Conexión
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

ingredient_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

if ingredient_list:
    ingredients_string = ''

    for fruit_chosen in ingredient_list:
        ingredients_string += fruit_chosen + ' '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)  
        sf_df= st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)


    clean_ingredients = ingredients_string.strip()

    my_insert_stmt = f""" insert into smoothies.public.orders(ingredients, name_on_order)
            values ('{clean_ingredients}', '{name_on_order}')"""
    
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Smoothie ordered, {name_on_order}!', icon="✅")
