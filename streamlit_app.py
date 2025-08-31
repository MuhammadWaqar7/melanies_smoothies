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

# CORRECTION 1: Remove the incorrect 'when_matched' import
# from snowflake.snowpark.functions import col, when_matched
cnx = st.connection('snowflake')
session = cnx.session()

my_dataframe = session.table('smoothies.public.fruit_options').select(col('FRUIT_NAME'),col('SEARCH_ON'))
pd_df=my_dataframe.to_pandas()

# CORRECTION 2: Get a list for the multiselect from the Pandas DataFrame
options_list = pd_df['FRUIT_NAME'].tolist()

# CORRECTION 3: Use the list 'options_list' instead of the DataFrame 'my_dataframe'
Ingredients_list = st.multiselect(
    'Choose up to 5 Ingredients:',
    options_list,
    max_selections=5
)

# CORRECTION 4 (MOST IMPORTANT): All code for handling the selection must be inside this IF block.
if Ingredients_list:
    Ingredients_string = ''
    
    for fruit_chosen in Ingredients_list:
        Ingredients_string += fruit_chosen + ' '
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + " Nutrition Information")
        # CORRECTION 5: Use the correct Fruityvice API URL
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        # Parse the JSON response into a DataFrame for a nicer display
        fv_df = pd.json_normalize(fruityvice_response.json())
        st.dataframe(data=fv_df, use_container_width=True)
    
    # --- THIS NEXT PART MUST BE INSIDE THE IF BLOCK BUT OUTSIDE THE FOR LOOP ---
    st.write(Ingredients_list)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + Ingredients_string + """','""" + name_on_order + """')"""

    st.write(my_insert_stmt)
    
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
