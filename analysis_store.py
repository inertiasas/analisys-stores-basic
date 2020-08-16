#!/usr/bin/env python
# coding: utf-8

# # Obtener la información de la tienda
# 
# Autor: Luis Camilo Jimenez, CEO
# 

# ## Librerías

# In[65]:


import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from sklearn import model_selection, naive_bayes, svm
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score


# ## Listado de productos

# In[38]:


term = 'lacteos'
url_search = 'https://busqueda.tiendasjumbo.co/busca?q={0}'.format(term)
search = requests.get(url_search)
soup_search = BeautifulSoup(search.text, "html5lib")
results = soup_search.find_all('h2',class_="nm-product-name")
print(results[:2])


# ## Información del producto
# 
# Extracción de información: Categorias, imagén, nombre, descripción, precio

# In[39]:


products = []
for index, result in enumerate(results):
    product = {}
    product["url"] = 'https:'+ result.a.get('href')
    # Obtiene la web page
    search_product = requests.get(product["url"])
    # Soup
    soup_product = BeautifulSoup(search_product.text, "html5lib")
    # Categorías 1 y 2
    lis = soup_product.find('div',class_="bread-crumb").find_all('li')
    product["category_1"] = lis[3].span.string
    product["category_2"] = lis[2].span.string
    # Imagen
    product["url_image"]=soup_product.find('div',id="image").a.get('href')
    # Nombre
    product["name"]=soup_product.find('div',class_="fn").string
    # Descripción
    product["description"]=soup_product.find('div',class_="productDescription").string
    # Precio
    product["price"]=soup_product.find('div',class_="plugin-preco").find('strong',class_="skuBestPrice").string
    # Incluir
    products.append(product)
    
print(json.dumps(products[:2], indent=4, sort_keys=True))


# # Analizar los productos
# 
# ## Extraer campos a analizar

# In[40]:


df = pd.DataFrame.from_dict(products)
col = ['category_1', 'name']
df = df[col]
print(df.head())


# ## Ajustar nombre y verficar datos

# In[41]:


df = df[pd.notnull(df['name'])]
df.columns = ['category', 'name']


# ## Codificar categoría como entero

# In[43]:


df['category_id'] = df['category'].factorize()[0]
category_id_df = df[['category', 'category_id']].drop_duplicates().sort_values('category_id')
category_to_id = dict(category_id_df.values)
id_to_category = dict(category_id_df[['category_id', 'category']].values)
print(category_id_df)


# ## Se generan los tokens

# In[44]:


df['name'] = [entry.lower() for entry in df['name']]
print(df.head())


# In[48]:


df['name']= [word_tokenize(entry) for entry in df['name']]
print(df.head())


# In[52]:


for index,entry in enumerate(df['name']):
    final_words = []
    stemmer = SnowballStemmer('spanish')
    for word in entry:
        if word not in stopwords.words('spanish') and word.isalpha():
            word_final = stemmer.stem(word)
            final_words.append(word_final)
            df.loc[index,'name'] = str(final_words)
print(df.head())


# # Modelo
# 
# ## Se dividen los valores en los de entrenamiento y testeo

# In[55]:


Train_X, Test_X, Train_Y, Test_Y = model_selection.train_test_split(df['name'],df['category'],test_size=0.3)


# In[58]:


Encoder = LabelEncoder()
Train_Y = Encoder.fit_transform(Train_Y)
Test_Y = Encoder.fit_transform(Test_Y)
print(Train_Y)


# In[62]:


Tfidf_vect = TfidfVectorizer(max_features=5000)
Tfidf_vect.fit(df['name'])
print(Tfidf_vect.vocabulary_)


# In[63]:


Train_X_Tfidf = Tfidf_vect.transform(Train_X)
Test_X_Tfidf = Tfidf_vect.transform(Test_X)
print(Train_X_Tfidf)


# ## Modelo SVM — Support Vector Machine

# In[66]:


SVM = svm.SVC(C=1.0, kernel='linear', degree=3, gamma='auto')
SVM.fit(Train_X_Tfidf,Train_Y)
predictions_SVM = SVM.predict(Test_X_Tfidf)
print("SVM Accuracy Score -> ",accuracy_score(predictions_SVM, Test_Y)*100)

