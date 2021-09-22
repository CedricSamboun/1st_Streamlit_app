import time
import streamlit as st
# importing numpy and pandas for to work with sample data.
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import plotly_express as px
import streamlit.components.v1 as components
from functools import wraps
# import time

def config():

    st.set_page_config(
        page_title = 'Dashboard Uber',
        layout = 'wide')
config()

def log_time(func):
    """This decorator prints the execution time for the decorated function."""

    @wraps(func)
    def wrapper(args, **kwargs):
        
        start = time.time()
        result = func(args, **kwargs)
        end = time.time()
        f = open("log_dev.txt",'a',encoding="utf8")
        time_res = end - start
        mes = "\n"+func.__name__+ " time = " + str(time_res) + " s" + " un temps plutçot correct"
        f.write(mes)
        return result

    return wrapper
#@st.cache  # 👈 This function will be cached
#def my_slow_function(arg1, arg2):
    # Do something really slow in here!
   # return the_output
# Si le programme ne fonctionne pas, mettre la ligne 16 à 19 en commentaire, j'ai ajouter cette ligne pour un peu plus d'interaction et mettre le site en dark    
st.title('You will find in this page the 2 dashboards')
@st.cache(allow_output_mutation=True)
@log_time
def read_(chemin):
    dataset=pd.read_csv(chemin)
    return dataset

@st.cache(allow_output_mutation=True)  
@log_time  
def read1_(chemin):

    dataset1=pd.read_csv(chemin)
    return dataset1

data = read_('ny-trips-data.csv')
df = read1_('uber-raw-data-apr14.csv')

#st.write(data)
#st.write(df)
def get_weekday(df):
    return df.weekday()

def get_dom(df):
    return df.day

def get_hours(df):
    return df.hour

def count_rows(rows):
    return len(rows)

def choix(arg1,arg2):
    choice = [arg1,arg2]
    return choice
choice = choix('2014-Apr-uber','New York Trips')    
df_map = pd.DataFrame()
data_map_dropoff = pd.DataFrame()
data_map_pickup = pd.DataFrame()

databar = pd.DataFrame(data[:], columns = ["Date/Time","Lat","Lon"])



#@st.cache(suppress_st_warning=True)
@log_time
def option(arg):
    data = read_('ny-trips-data.csv')
    df = read1_('uber-raw-data-apr14.csv')

    option = st.sidebar.selectbox(arg,choice)

    st.set_option('deprecation.showPyplotGlobalUse', False)
    if option == choice[0]:

        st.title('Here is ubers April 2014 Dashboard')
        
        st.text("Beginning of raw dataset")
        st.write(df.head(15))
        header_1_column, header_2_column, header_3_column = st.columns(3)

        date_debut = header_1_column.date_input(
            "Starting date",
            datetime.date(2014, 4, 1))

        date_fin = header_2_column.date_input(
            "Ending date",
            datetime.date(2014, 4, 30))

        pressed = header_3_column.button('Search')
        
        if pressed:
            mask = (df['Date/Time'].dt.date > date_debut) & (df['Date/Time'].dt.date <= date_fin)
            df = df.loc[mask]
            

        df['Date/Time']=pd.to_datetime(df['Date/Time'])
        df['hours']= df['Date/Time'].map(get_hours)
        df['dom']= df['Date/Time'].map(get_dom)
        df['weekday']= df['Date/Time'].map(get_weekday)
        
        st.header('Map of pickups/dropoffs')

        df_map['lon'] = df['Lon']
        df_map['lat'] = df['Lat']
        
        st.map(df_map)
        st.header('Heatmap')
        
        dataByDayAndHours = df.groupby(['weekday','hours']).apply(count_rows).unstack()
        fig4, ax = plt.subplots()
        sns.heatmap(dataByDayAndHours, linewidths = .5)
        st.pyplot(fig4)

        frqDay1_column = st.columns(2)
        st.header('Histograms')
        df[["dom"]].plot.hist(bins = 30, rwidth=0.8, range=(0.5,30.5), figsize = (30,15) , title = "Pick - Fréquence des course par jour - Uber - April 2014")
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot()
    
      
        
    elif option == choice[1]:
        st.title('Here is New York Trips Dashboard')
    
        st.text("Beginning of raw dataset")
        st.write(data.head(15))

        header_1_column, header_2_column, header_3_column = st.columns(3)

        date_debut = header_1_column.date_input(
            "Starting date",
            datetime.date(2014, 4, 1))

        date_fin = header_2_column.date_input(
            "Ending date",
            datetime.date(2014, 4, 30))

        pressed = header_3_column.button('Search')
      
        if pressed:
            mask = (data['Date/Time'].dt.date > date_debut) & (data['Date/Time'].dt.date <= date_fin)
            data = df.loc[mask]
            
        
        
        data['tpep_pickup_datetime']=pd.to_datetime(data['tpep_pickup_datetime'])
        data['tpep_dropoff_datetime']=pd.to_datetime(data['tpep_dropoff_datetime'])
        data['hours-pickup']= data['tpep_pickup_datetime'].map(get_hours)
        data['hours-drop']= data['tpep_dropoff_datetime'].map(get_hours)
        data['dom-pickup']= data['tpep_pickup_datetime'].map(get_dom)
        data['dom-drop']= data['tpep_dropoff_datetime'].map(get_dom)
        data['weekday-pickup']= data['tpep_pickup_datetime'].map(get_weekday)
        data['weekday-drop']= data['tpep_dropoff_datetime'].map(get_weekday)
        
        st.header('Map of pickups')
        data_map_dropoff['lon'] = data['dropoff_longitude']
        data_map_dropoff['lat'] = data['dropoff_latitude']
        st.map(data_map_dropoff)
        
        st.header('Map of dropoffs')
        data_map_pickup['lon'] = data['pickup_longitude']
        data_map_pickup['lat'] = data['pickup_latitude']
        st.map(data_map_pickup)

      
        by_passenger_count= data.groupby('passenger_count').mean()
        st.write(by_passenger_count)
        st.title('Number of passengers considering the travelled distance')
        graph=px.bar(by_passenger_count,y="trip_distance")
        st.plotly_chart(graph)
        

        frqDay_1_column, frqDay_2_column = st.columns(2)
        frqDay_1_column.text('Clients supporting')
        data[["dom-pickup"]].plot.hist(bins = 30, rwidth=0.8, range=(0.5,30.5), figsize = (30,15) , title = "Frequency of pickups by day")
        st.set_option('deprecation.showPyplotGlobalUse', False)
        
        frqDay_1_column.pyplot()
        st.title("Frenquency by day")
        frqDay_2_column.text('Dépôt des clients')
        data[["dom-drop"]].plot.hist(bins = 30, rwidth=0.8, range=(0.5,30.5), figsize = (30,15) , title = "Frequency of dropoff by day")
        st.set_option('deprecation.showPyplotGlobalUse', False)
    
        frqDay_2_column.pyplot()
    
        dataByDayAndHoursDrop = data.groupby(['weekday-pickup','hours-pickup']).apply(count_rows).unstack()
        fig4, ax = plt.subplots()
        sns.heatmap(dataByDayAndHoursDrop, linewidths = .5)
        st.pyplot(fig4)
        
        dataByDayAndHoursDrop = data.groupby(['weekday-drop','hours-drop']).apply(count_rows).unstack()
        fig4, ax = plt.subplots()
        sns.heatmap(dataByDayAndHoursDrop, linewidths = .5)
        st.pyplot(fig4)
        st.title("Frequency by hour")

option('Choose a dataset')    
components.html("""

<div class="max-w-sm  overflow-hidden shadow-lg mx-auto my-8">
    <img class="w-full" src="https://t4.ftcdn.net/jpg/00/87/28/85/360_F_87288547_iMGD9Z7C5xMOq4auyvySnqB1bk083NAc.jpg" alt="Sunset in the mountains">
    <div class="px-6 py-4">
  <span style="color:red">Here you will find all the information you need about uber's pickups and dropoffs. Use it efficiently!</span>
      <p class="text-red-800 text-base">
        
      </p>
    </div>
    <div class="px-6 py-4">
     
      
    </div>
  </div>
      </div>
    """,
    height=700,

)


