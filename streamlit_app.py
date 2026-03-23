import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title(":apple: Customize Your Smoothie! :strawberry:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Smoothie name:")
st.write("The name of the Smoothie is:", name_on_order)

# Conexión
cnx = st.connection("snowflake")
session = cnx.session()

# 1. Traemos AMBAS columnas y convertimos a Pandas para que .loc funcione
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

ingredient_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe, # Snowpark manejará el despliegue de FRUIT_NAME automáticamente
    max_selections=5
)

if ingredient_list:
    ingredients_string = ''

    for fruit_chosen in ingredient_list:
        ingredients_string += fruit_chosen + ' '
        
        # 2. Buscamos el valor de SEARCH_ON usando el DataFrame de Pandas (pd_df)
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        
        # 3. Usamos la variable search_on en la URL de la API
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    clean_ingredients = ingredients_string.strip()

    my_insert_stmt = f""" insert into smoothies.public.orders(ingredients, name_on_order)
            values ('{clean_ingredients}', '{name_on_order}')"""
    
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'✅ Smoothie ordered, {name_on_order}!', icon="✅")

import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, when_matched

st.title(f":apple: Pending Smoothie Order :strawberry:")

cnx = st.connection("snowflake")
session = cnx.session()

# TRAER DATOS (Sin .collect())
# .to_pandas() es clave aquí para que el editor de datos funcione bien
my_dataframe = session.table("smoothies.public.orders").filter(col("ORDER_FILLED") == 0).to_pandas()

# EDITAR DATOS
editable_df = st.data_editor(my_dataframe)

submited = st.button('Submit')

if submited:
    try:
        # Convertir el DataFrame de Pandas editado de vuelta a Snowpark
        edited_dataset = session.create_dataframe(editable_df)
        
        og_dataset = session.table("smoothies.public.orders")
        
        # Realizar el MERGE
        og_dataset.merge(edited_dataset
                         , (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID'])
                         , [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
                        )
        st.success('Order(s) Updated!', icon="👍")
    except Exception as e:
        st.error(f'Something went wrong: {e}')
