#import necessary libraries
import streamlit as st
import easyocr
import mysql.connector
import cv2
import numpy as np 
import pandas as pd
from mysql.connector import Error
import json
from PIL import Image
import requests
from streamlit_lottie import st_lottie
# Connect to MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Logeesh@04",
    database="logu")

mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE IF NOT EXISTS bus (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), job_title VARCHAR(255), address VARCHAR(255), postcode VARCHAR(255), phone VARCHAR(255), email VARCHAR(255), website VARCHAR(255), company_name VARCHAR(225))")


reader = easyocr.Reader(['en'])

#Animations 
def load_lottieur(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()  
lottie_coding = load_lottieur("https://assets1.lottiefiles.com/packages/lf20_830nh3fg.json")  


#title 
left_column,right_column = st.columns(2)
with left_column:
    st.title(":blue[BizCardX: Card Scanner]")
with right_column:
    st_lottie(lottie_coding,height=200, key='codings')


#Dropdown mwnu
menu = ['Extract', 'Display', 'download']
choice = st.selectbox("Select an option", menu)


#uploading the photo
uploaded_file = st.file_uploader("Upload a business card image", type=["jpg", "jpeg", "png"])




if choice == 'Extract':
    if uploaded_file is not None:
        image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), 1)
        st.image(image, caption='Uploaded business card image', use_column_width=True)
        if st.button('Extract Information'):  
            bounds = reader.readtext(image, detail=0)  
            text = "\n".join(bounds)
            sql = "INSERT INTO bus(name, job_title, address, postcode, phone, email, website, company_name) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (bounds[0], bounds[1], bounds[2], bounds[3], bounds[4], bounds[5], bounds[6], bounds[7])
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Business card information added to database.")


#----------------------------------------------------------------------------------------
elif choice == 'Display':   
   mycursor.execute("SELECT * FROM bus")
   result = mycursor.fetchall()
   df = pd.DataFrame(result, columns=['id','name', 'job_title', 'address', 'postcode', 'phone', 'email', 'website', 'company_name'])
   st.write(df)

#-----------------------------------------------------------------------------------------
elif choice == 'download':
    col1, col2 = st.columns(2)
    with col1:
      st.write("Download the tweet data as CSV File")
      # save the documents in a dataframe
      mycursor.execute("SELECT * FROM bus")
      result = mycursor.fetchall()
      df = pd.DataFrame(result, columns=['id','name', 'job_title', 'address', 'postcode', 'phone', 'email', 'website', 'company_name'])
      # Convert dataframe to csv
      df.to_csv('card_data.csv')
      def convert_df(data):
        # Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')
      csv = convert_df(df)
      st.download_button(
                        label="Download data as CSV",
                        data=csv,
                        file_name='card_data.csv',
                        mime='text/csv',
                        )
      st.success("Successfully Downloaded data as CSV")

    # Download the scraped data as JSON
    with col2:
      st.write("Download the tweet data as JSON File")
      # Convert dataframe to json string instead as json file 
      twtjs = df.to_json(default_handler=str).encode()
      # Create Python object from JSON string data
      obj = json.loads(twtjs)
      js = json.dumps(obj, indent=4)
      st.download_button(
                        label="Download data as JSON",
                        data=js,
                        file_name='twtjs.js',
                        mime='text/js',
                        )
      st.success("Successfully Downloaded data as JSON")