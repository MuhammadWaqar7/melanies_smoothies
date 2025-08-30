# Import python packages
import requests
import pandas as pd
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
# my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_Name'),col('Search_on'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()
my_dataframe = session.table('smoothies.public.fruit_options').select(col('FRUIT_NAME'),col('SEARCH_ON'))
pd_df=my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()
Ingredients_list = st.multiselect(
    'Choose up to 5 Ingredients:',
    my_dataframe,
    max_selections=5
)

if Ingredients_list:
    Ingredients_string = ''
    for fruit_chosen in Ingredients_list:  # Fixed variable name (capital I)
        Ingredients_string += fruit_chosen + ' * '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        st.subheader(fruit_chosen + " Nutrition Information")
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        # fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
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




# my_dataframe = session.table('smoothies.public.fruit_options').select(col('FRUIT_NAME'),col('SEARCH_ON'))
# pd_df=my_dataframe.to_pandas()

# # ... later in the loop ...
# search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
