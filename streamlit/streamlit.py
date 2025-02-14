import streamlit as st
from snowflake.snowpark.context import get_active_session

# Display the logo as the title
st.markdown(
    """
    <div style="text-align: center;">
        <img src="https://logowik.com/content/uploads/images/siemens-energy-bg-white8861.logowik.com.webp" alt="Logo" style="width: 100px; margin-bottom: 10px;">

    """,
    unsafe_allow_html=True
)

# Get the active session
session = get_active_session()

# Query to get the unique 'keyv' values
query = "SELECT DISTINCT keyv FROM FINANCE"
keyv_data = session.sql(query).to_pandas()

# Select box to choose the keyv
selected_keyv = st.selectbox("Select a Key Value (keyv)", keyv_data['KEYV'].tolist())

# Fetch the corresponding value for the selected keyv
query_value = f"SELECT BRAND FROM FINANCE WHERE KEYV = '{selected_keyv}'"
value_data = session.sql(query_value).to_pandas()

# Initialize session state for clearing the text input
if "new_value" not in st.session_state:
    st.session_state.new_value = ""

if not value_data.empty:
    current_value = value_data['BRAND'].iloc[0]
    st.write(f"Current brand for keyv {selected_keyv}: {current_value}")
    
    # Text box to input a new value
    new_value = st.text_input(f"Enter a new brand for keyv {selected_keyv}:", st.session_state.new_value)

    # Submit button to update the value in Snowflake
    if st.button("Submit"):
        if new_value and new_value != current_value:
            # Update the value in Snowflake
            update_query = f"UPDATE FINANCE SET BRAND = '{new_value}' WHERE KEYV = '{selected_keyv}'"
            try:
                session.sql(update_query).collect()
                st.success(f"Successfully updated brand for keyv {selected_keyv} to {new_value}")
                
                # Clear the text input field after submit
                st.session_state.new_value = ""
                st.rerun()  # Refresh UI to reset input
            except Exception as e:
                st.error(f"Error updating brand: {e}")
        else:
            st.warning("The brand is either empty or the same as the current value, no update needed.")
else:
    st.warning("No data found for the selected keyv.")

# Display the full data in a dataframe (optional)
st.subheader("Finance Table Data")
data_query = "SELECT * FROM FINANCE LIMIT 20"
data_df = session.sql(data_query).to_pandas()
st.dataframe(data_df, use_container_width=True)
