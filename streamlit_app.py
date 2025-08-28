# Import python packages
import requests
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("Customize Your Smoothie! 🥤")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    [docs.streamlit.io](https://docs.streamlit.io).
    """
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

from snowflake.snowpark.functions import col, when_matched

cnx = st.connection('snowflake')
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_Name'))

Ingredients_list = st.multiselect(
    'Choose up to 5 Ingredients:',
    my_dataframe,
    max_selections=5
)

if Ingredients_list:
    Ingredients_string = ''
    for fruit_chosen in Ingredients_list:  # Fixed variable name (capital I)
        Ingredients_string += fruit_chosen + ' * '
        st.subheader(fruit_chosen + " Nutrition Information")
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    
    # This was incorrectly indented inside the for loop
    st.write(Ingredients_list)

    my_insert_stmt = """ insert into smoothies.public.orders(Ingredients,Name_on_Order)
            values ('""" + Ingredients_string + """','""" + name_on_order + """')"""

    st.write(my_insert_stmt)
    
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
