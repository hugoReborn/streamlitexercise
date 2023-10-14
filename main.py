import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk
import plotly.express as px



DATA_URL = (
    "Motor_Vehicle_Collisions_-_Crashes.csv"
)

st.title("Cantidad De Colisiones En La Ciudad De New York ")
st.markdown("## Esta Aplicacion Esta Construida Con Streamlit Para Analizar Colisiones En NYC ")


@st.cache(persist=True)  # decorator , one time data load
def load_data(nrows):
    # almacenaremos los datos en nuestra variable data y leeremos este archivo con pandas read
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    # el primer argunmento sera el path del archivo o la url de donde estamos sacando los datos
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    # los datos tiene unas columnas , que es la fecha del choque y la hora del choque
    lowercase = lambda x: str(x).lower()
    # usamos un parse dates para convertirlas en formato datetime indicamos las columnas que pasaremos al parse dates
    data.rename(lowercase, axis='columns', inplace=True)
    # tomamos los na datos  almacenados en el data
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)
    return data


data = load_data(100000)  # cantidad de filas que se mostraran en la aplicacion

# paso 3 hacer preguntas a los datos y graficarlos
st.header("Cantidad De Lesionados Por Colision?")
injured_people = st.slider("Numero de Personas Lesionadas", 0,
                           19)  # buscaremos gente lesionada y usaremos un slider de Streamlit 0 minimo de herido #19 el maximo
# mostrar los datos en un mapa
st.map(data.query("injured_persons >=@injured_people")[["latitude", "longitude"]].dropna(
    how="any"))  # FILTRAMOS LA DATA dependiendo de los dañados usando la funcion query y necesitamos la longitud y la latitud para ponerlas en un mapa

# paso 4 preguntar cuantas colisiones hay en un dia

st.header("Cuantas Colisiones Ocurren En Determinado Horario?")
hour = st.slider("Hora Seleccionada", 0, 23)  # rango hora de las 0 a las 24 y separadas por un valor de 1
data = data[data['date/time'].dt.hour == hour]

# parte 5 Mapa Interactivo
st.markdown("### Colisiones  entre %i:00 and %i:00" % (
hour, (hour + 1) % 24))  # subtitulo interactivo que se modifica a medida que se modifica la hora en el slider
midpoint = (
np.average(data['latitude']), np.average(data['longitude']))  # coordenadas iniciales para cuando el mapa se inicie
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,

    },
    # parte 6 mapa 3d interactivo p2
    layers=[  # especificado en una lista
        pdk.Layer(
            "HexagonLayer",
            data=data[['date/time', 'latitude', 'longitude']],  # subset de data
            get_position=['longitude', 'latitude'],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000],

        ),
    ],
))


#parte 7 tablaas e histogramas usaremos plotli
st.subheader("Colisiones Por Minuto Entre %i:00 and %i:00" % (hour, (hour + 1) %24))
# creando un nuevo dataframe filtrando datos
filtered = data[
    #filtramos los datos de la columna date/time y mostramos la hora , mas la hora +1
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))

]
# creando histograma
#le pasamos los datos filtrados y ahora vemos por minutos dentro del filtro
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
#creamos otro dataframe que plotly pueda usar, en el data frame, la primera columna
#segunda columna son los valores en hist, number of crashes
#crashes es el eje Y
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
#ahora crearemos una figura plotli
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)
# lo que acabamos de hacer nuestra los datos de manera raw , los datos duros generalmente se usan para
# tareas de debuggins l lo que haremos ahora es esconder estos datos duros y que se muestren solo pinchando
# un check box
if st.checkbox("Mostrar Datos RAW", False):
    st.subheader('Raw Data')  # subtitulo
    st.write(data)  # envia a que se muestre la data en la app
