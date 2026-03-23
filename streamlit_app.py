# Import python packages
import streamlit as st

# Write directly to the app
st.title(f":apple: Customize Your Smoothie! :strawberry:")
st.write(
  """ Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order = st.text_input(f"Smoothie name:")
st.write(
  """ The name of the Smoothie is:
  """, name_on_order
)

from snowflake.snowpark.functions import col
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredient_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
)


# ... (código anterior igual)

if ingredient_list:
    ingredients_string = ''
    for fruit_chosen in ingredient_list:
        ingredients_string += fruit_chosen + ' '
    
    # Quitamos el espacio sobrante al final
    clean_ingredients = ingredients_string.strip()

    # Construimos el insert asegurando que los nombres coincidan con tu tabla
    my_insert_stmt = f"""insert into smoothies.public.orders(ingredients, name_on_order)
            values ('{clean_ingredients}', '{name_on_order}')"""
    
    # OPCIONAL: Descomenta la línea de abajo para ver el SQL exacto en la app si falla
    # st.write(my_insert_stmt)

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        if name_on_order: # Verificamos que no esté vacío
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie "{name_on_order}" is ordered!', icon="✅")
        else:
            st.warning("Please add a name for the smoothie.")



