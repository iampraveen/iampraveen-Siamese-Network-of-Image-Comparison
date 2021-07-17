import streamlit as st
import pandas as pd
from db import Image
import os
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import tensorflow as tf
from sqlalchemy import create_engine, Column, Integer,String,DateTime
from sqlalchemy.ext import declarative
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from PIL import Image as ImageClass,ImageOps
import numpy as np

def opendb():
    engine = create_engine('sqlite:///db.sqlite3') # connect
    Session =  sessionmaker(bind=engine)
    return Session()

def save_file(file,path):
    try:
        db = opendb()
        ext = file.type.split('/')[1] # second piece
        img = Image(filename=file.name,extension=ext,filepath=path)
        db.add(img)
        db.commit()
        db.close()
        return True
    except Exception as e:
        st.write("database error:",e)
        return False

def load_model():
  ffm = tf.keras.models.load_model('fashion_feature_model.h5')
  fsm = tf.keras.models.load_model('fashion_similarity_model.h5')
  return ffm,fsm

ffm,fsm = load_model()

st.markdown('''
<style>
#seamese-network-of-image-comparission{color:black}
</style>
<h1 id = "item">
Seamese Network Of Image Comparission
''',unsafe_allow_html = True )

st.info('*this is seamese network of image comparission,It Compaier the image , text and video*')
st.subheader("Upload the data")

options = ['Upload image','compare images','Delete Record']
ch = st.selectbox("",options)
if ch =='Upload image':
    file = st.file_uploader("select a image",type=['jpg','png'])
    if file is not None:
      if file and st.button('Upload'):
        file_details = {"FileName":file.name,"FileType":file.type,"FileSize":file.size}
        st.write(file_details)
        path = os.path.join('uploads',file.name)
        with open(path,'wb') as f:
          f.write(file.getbuffer())
          status = save_file(file,path)
          if status:
            st.sidebar.success("file uploaded")
            st.sidebar.image(path,use_column_width=True)
          else:
            st.sidebar.error('upload failed')


if ch == 'compare images':
  db = opendb()
  results = db.query(Image).all()
  db.close()
  col1,col2 = st.beta_columns(2)
  img = col1.selectbox('select image',results)
  img2 = col2.selectbox('select image 2',results)
  if img and os.path.exists(img.filepath):
    col1.info("image selected ")
    col1.image(img.filepath, use_column_width=True)
  if img2 and os.path.exists(img2.filepath):
    col2.info("image 2 selected ")
    col2.image(img2.filepath, use_column_width=True)
  if st.button("Compare"):
    imgA = ImageClass.open(img.filepath)
    imgB = ImageClass.open(img2.filepath)
    imgA = imgA.resize((28,28)).convert('L')
    imgB = imgB.resize((28,28)).convert('L')
    imgA = ImageOps.invert(imgA)
    imgB = ImageOps.invert(imgB)
    col1.image(imgA)
    col2.image(imgB)
    img_a = np.array(imgA).reshape(1,28,28,1)
    img_b = np.array(imgB).reshape(1,28,28,1)
    input_data = [img_a,img_b]
    # hadd h
    out = fsm.predict(input_data)
    st.success(f"both images are {out[0][0]*100:.2f}% similar types")


if ch == 'Delete Record':
  db = opendb()
  results = db.query(Image).all()
  db.close()
  img = st.sidebar.radio('select image to remove',results)
  if img:
      st.error("img to be deleted")
      if os.path.exists(img.filepath):
        st.image(img.filepath, use_column_width=True)
      if st.sidebar.button("delete"): 
        try:
            db = opendb()
            db.query(Image).filter(Image.id == img.id).delete()
            if os.path.exists(img.filepath):
              os.unlink(img.filepathP)
            db.commit()
            db.close()
            st.info("image deleted")
        except Exception as e:
            st.error("image not deleted")
            st.error(e)





main_bg = "e1115afea56dcaf0c273a4f3d9fc7f3a.jpg"
main_bg_ext = "jpg"

side_bg = "e1115afea56dcaf0c273a4f3d9fc7f3a.jpg"
side_bg_ext = "jpg"

with open("style.css") as f:
    st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)