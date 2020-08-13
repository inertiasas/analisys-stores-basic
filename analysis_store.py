#!/usr/bin/env python
# coding: utf-8

# # Obtener la información de la tienda
# 
# Autor: Luis Camilo Jimenez, CEO
# 

# ## Librerías

# In[1]:


import requests
from bs4 import BeautifulSoup
import json
import pandas as pd


# ## Listado de productos

# In[2]:


term = 'leche'
url_search = 'https://busqueda.tiendasjumbo.co/busca?q={0}'.format(term)
search = requests.get(url_search)
soup_search = BeautifulSoup(search.text, "html5lib")
results = soup_search.find_all('h2',class_="nm-product-name")
print(results[:2])


# ## Información del producto
# 
# Extracción de información: Categorias, imagén, nombre, descripción, precio

# In[3]:


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

# In[8]:


df = pd.DataFrame.from_dict(products)
col = ['category_1', 'name']
df = df[col]
print(df.head())


# In[9]:


df = df[pd.notnull(df['name'])]
df.columns = ['category', 'name']


# # Agregaremos una columna que codificará la categoría como un entero
