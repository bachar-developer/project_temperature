import pandas as pd 
import requests as rq
import json 
import unicodedata
import datetime
import matplotlib.pyplot as plt
 

### Capa 1 Lectura del archivo csv localizar la columna referente al id de los pueblos 

documento=pd.read_csv('clientes.csv',sep=';',header=None,)
cp=documento[4].dropna().astype(str).unique()
pueblos=documento[5].dropna().astype(str).unique()

cp_limpios=[]

for i in cp:
        i=i[:-2]
        if  len(i)==5:
            cp_limpios.append(i)

provincias = [
    "alava","albacete","alicante","almeria","asturias","avila","badajoz","barcelona",
    "burgos","caceres","cadiz","cantabria","castellon","ceuta","ciudad-real","cordoba",
    "cuenca","girona","granada","guadalajara","guipuzcoa","huelva","huesca",
    "illes-balears","jaen","la-coruna","la-rioja","las-palmas","leon","lleida",
    "lugo","madrid","malaga","melilla","murcia","navarra","ourense","palencia",
    "pontevedra","salamanca","segovia","sevilla","soria","tarragona",
    "santa-cruz-de-tenerife","teruel","toledo","valencia","valladolid",
    "vizcaya","zamora","zaragoza"
]
### capa 1b Crear filtros para el csv sucio 

primer_filtro=[]##normaliza el dato quitando acentos etc 

for pueblo in pueblos:
    pueblo_normalizado=""
    n_pueblo=pueblo.strip().replace(' ','-').lower()
    for letra in n_pueblo:
        normalizada=unicodedata.normalize('NFKD',letra)
        for caracter in normalizada:
            if unicodedata.category(caracter)!='Mn'and caracter not in '0123456789!",·$%&/(=?¿`) ' and caracter not in ' ':
                pueblo_normalizado=pueblo_normalizado+caracter


    
    if pueblo_normalizado not in primer_filtro:
        primer_filtro.append(pueblo_normalizado)
        


segundo_filtro=[]##Elimina los patrones que tienen asociado en el nombre la capital 



for nombre_pueblo in primer_filtro:
    n_arreglado=''
    n_separado=nombre_pueblo.split('-')
    temp=[]
    for n_parte in n_separado:
        if n_parte not in temp:
            temp.append(n_parte)
            if n_parte not in provincias:
                n_arreglado=n_arreglado+n_parte+'-'      
        


           

    segundo_filtro.append(n_arreglado[:-1])


tercer_filtro=[i for i in segundo_filtro if i]## con la compresion de lista si i = cadena vacia entonces es false lo cual lo saca de la lista

##Capa 2 Obtener datos clima  de la url 

dic_resultados={}

hora_guardado=datetime.datetime.now().strftime('%d_%H.%M.%S')

temperaturas=[]
humedad_p=[]

for pueblo in tercer_filtro:
    
    response=rq.get(f'https://www.eltiempo.es/{pueblo}.html')## peticion al inspeccionar 
    posicion_t=response.text.find('ºC')##busco la posicion mediante find 
    temperatura=int(response.text[posicion_t+len('ºC')-4:posicion_t+len('ºC')-2])##concentro la busqueda en lo que me interesa de la temperatura
    temperaturas.append(temperatura)
    posicion_h=response.text.find('humidity')##busco la humedad
    humedad=int(response.text[posicion_h+11:posicion_h+13])##concentro la busqueda en la humedad 
    humedad_p.append(humedad)
    dic_resultados[pueblo]={'temperatura':temperatura ,'humedad':humedad}##guardo todo en un diccionario interno

# # Capa 2b Guardo las temperaturas 

with open(f'registro_{hora_guardado}.json','w') as f:
 json.dump(dic_resultados,f,indent=4)



### capa 3 Relacionar pueblos y datos meteorologicos
pueblos=[]
for pueblo in tercer_filtro:
    if '-' in pueblo:
        n_pueblo=pueblo.replace('-',' ').title()
        pueblos.append(n_pueblo)
    elif '-' not in pueblo:
        pueblos.append(pueblo.capitalize())


plt.figure(figsize=(15,6))
plt.barh(pueblos,temperaturas,color='black')
plt.yticks(pueblos,fontsize=8)
plt.title('TEMPERATURAS DEL ALJARAFE')
plt.xlabel('Temperaturas',loc='center')
plt.ylabel('Pueblos')
plt.show()

