import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración inicial
st.set_page_config(page_title="F1 2025: El Fin de una Era", layout="wide")

#PARTE 1: OBTENCIÓN, LIMPIEZA Y TRANSFORMACIÓN DE DATOS
@st.cache_data
def load_and_clean_data():
    race_df = pd.read_csv('Formula1_2025Season_RaceResults.csv')
    sprint_df = pd.read_csv('Formula1_2025Season_SprintResults.csv')
    track_order = race_df['Track'].unique()
    track_to_round = {track: i+1 for i, track in enumerate(track_order)}
    race_points = race_df.groupby(['Track', 'Driver'])['Points'].sum().reset_index()
    sprint_points = sprint_df.groupby(['Track', 'Driver'])['Points'].sum().reset_index()
    
    total_points = pd.merge(race_points, sprint_points, 
                            on=['Track', 'Driver'], 
                            how='outer', 
                            suffixes=('_race', '_sprint')
                            ).fillna(0)
    total_points['Total_Points'] = total_points['Points_race'] + total_points['Points_sprint']
    total_points['Round'] = total_points['Track'].map(track_to_round)
    driver_pivot = total_points.pivot(index='Round', 
                                      columns='Driver', 
                                      values='Total_Points'
                                      ).fillna(0).sort_index()
    driver_cum = driver_pivot.cumsum()
    driver_cum['Track'] = track_order
    
    team_race = race_df.groupby(['Track', 'Team'])['Points'].sum().reset_index()
    team_sprint = sprint_df.groupby(['Track', 'Team'])['Points'].sum().reset_index()
    team_total = pd.merge(team_race, team_sprint, on=['Track', 'Team'], how='outer').fillna(0)
    team_total['Total_Points'] = team_total['Points_x'] + team_total['Points_y']
    team_total['Round'] = team_total['Track'].map(track_to_round)
    
    team_pivot = team_total.pivot(index='Round', 
                                  columns='Team', 
                                  values='Total_Points').fillna(0).sort_index()
    team_cum = team_pivot.cumsum()
    team_cum['Track'] = track_order
    
    race_clean = race_df[~race_df['Position'].isin(['NC', 'DQ'])].copy()
    race_clean['Position'] = race_clean['Position'].astype(int)
    race_clean['Posiciones_Ganadas'] = race_clean['Starting Grid'] - race_clean['Position']
    
    return driver_cum, team_cum, race_clean

driver_cum, team_cum, race_clean = load_and_clean_data()

#Parte 2: VISUALIZACIÓN DE DATOS Y NARRATIVA
#Título y descripción
st.title("🏎️ F1 2025: El Fin de la Era Red Bull")
st.info("**Pregunta de Investigación:** ¿Fue la temporada 2025 el año del cambio de guardia definitivo en la Fórmula 1, donde el trabajo en equipo superó al talento individual?")
st.markdown("""
Desde 2021, la Fórmula 1 fue sinónimo de un solo nombre: Max Verstappen. El dominio técnico de Red Bull Racing estableció récords históricos que parecían imposibles de replicar bajo el actual reglamento. Parecía que el campeonato estaba decidido antes de apagar los semáforos en la primera carrera. 

Sin embargo, los datos oficiales de la temporada 2025 revelan una historia completamente distinta. Fue un año marcado por la resiliencia, el desarrollo técnico agresivo y batallas estratégicas que cambiaron por completo el panorama de la máxima categoría del automovilismo.
            
A diferencia de un tablero de datos tradicional, en este artículo interactivo no solo veremos números fríos. Analizaremos la anatomía de una temporada histórica a través de la evidencia real de los circuitos, estructurada en tres actos:

1. **La Lucha Individual:** El asedio de Lando Norris y el bloque de McLaren sobre el trono de Verstappen.
2. **El Factor Sprint:** Cómo el ritmo puro sin paradas en pits inclinó la balanza en los fines de semana clave.
3. **La Caída del Imperio:** La prueba definitiva en el Campeonato de Constructores de que la consistencia de dos pilotos puede derrocar a un líder solitario.

Acompáñame a explorar los datos carrera a carrera y descubre dónde, cuándo y cómo cambió el equilibrio de poder en la Fórmula 1.
""")

st.divider()

#Colores para los pilotos
colores_f1 = {
    'Max Verstappen': "#023071",    #Red Bull Racing Honda RBPT     
    'Lando Norris': '#FF8000',      #McLaren Mercedes     
    'Oscar Piastri': '#FFB347',     #McLaren Mercedes    
    'Charles Leclerc': '#E8002D',   #Ferrari    
    'George Russell': '#27F4D2',    #Mercedes    
    'Lewis Hamilton': "#A10000",    #Ferrari    
    'Carlos Sainz': "#0381F6",      #Williams Mercedes
    'Yuki Tsunoda': "#0D3055",      #Red Bull Racing Honda RBPT
    'Kimi Antonelli': "#00FFD0",    #Mercedes
    'Fernando Alonso': "#229971",   #Aston Martin Aramco Mercedes
    'Lance Stroll': "#046343",      #Aston Martin Aramco Mercedes
    'Gabriel Bortoleto': "#129D00", #Kick Sauber Ferrari
    'Nico Hulkenberg': "#00B303",   #Kick Sauber Ferrari
    'Liam Lawson': "#F7F72F",       #Visa Cash App RB Honda RBPT
    'Isack Hadjar': "#AEA504",      #Visa Cash App RB Honda RBPT
    'Pierre Gasly': "#760792",      #Alpine Renault
    'Franco Colapinto': "#D205FA",  #Alpine Renault
    'Jack Doohan': "#5C087F",       #Alpine Renault
    'Esteban Ocon': "#9F9F9F",      #Haas Ferrari
    'Oliver Bearman': "#B6BABD"     #Haas Ferrari
}

#VISUALIZACIÓN 1: CAMPEONATO DE PILOTOS
st.header("1. La Lucha Individual: Campeonato de Pilotos")

top_5_pilotos = ['Lando Norris', 
                 'Max Verstappen', 
                 'Oscar Piastri', 
                 'George Russell', 
                 'Charles Leclerc']

#Selector de pilotos para comparar su evolución
pilotos_seleccionados = st.multiselect(
    "Selecciona los pilotos para comparar su evolución:",
    options=driver_cum.columns.drop('Track').tolist(),
    default=top_5_pilotos
)

if pilotos_seleccionados:
    fig_drivers = px.line(
        driver_cum, 
        x='Track', 
        y=pilotos_seleccionados,
        title="Evolución de Puntos Acumulados (2025)",
        labels={'value': 'Puntos Totales', 'Track': 'Gran Premio'},
        markers=True,
        color_discrete_map=colores_f1
    )
    
    fig_drivers.update_traces(line=dict(width=3), marker=dict(size=8))
    
    st.plotly_chart(fig_drivers, use_container_width=True)

#VISUALIZACIÓN 2: EL FACTOR SPRINT
st.header("2. Ritmo Puro: El Factor de las Carreras Sprint")
st.markdown("""
Las carreras Sprint son pruebas cortas de máxima velocidad sin paradas en pits obligatorias. 
Son el mejor termómetro del ritmo puro de un monoplaza. ¿Qué equipo logró sacar ventaja en este formato 
para sumar puntos críticos en el campeonato?
""")

@st.cache_data
def load_sprint_analysis():
    sprint_df = pd.read_csv('Formula1_2025Season_SprintResults.csv')
    return sprint_df

sprint_data = load_sprint_analysis()

#Selector de sede Sprint o vista global
opciones_sprint = ['Vista Global (Total de Puntos)'] + list(sprint_data['Track'].unique())
sede_sprint = st.selectbox(
    "Analiza el rendimiento en Sprint:",
    options=opciones_sprint
)

if sede_sprint == 'Vista Global (Total de Puntos)':
    df_plot = sprint_data.groupby('Driver')['Points'].sum().reset_index()
    df_plot = df_plot[df_plot['Points'] > 0].sort_values(by='Points', ascending=False)
    titulo_grafica = "Puntos Totales Acumulados en Formato Sprint (2025)"
else:
    df_plot = sprint_data[sprint_data['Track'] == sede_sprint].sort_values(by='Points', ascending=False)
    df_plot = df_plot[df_plot['Points'] > 0]
    titulo_grafica = f"Resultados de la Carrera Sprint en {sede_sprint}"

fig_sprint = px.bar(
    df_plot,
    x='Driver',
    y='Points',
    color='Driver',
    title=titulo_grafica,
    labels={'Points': 'Puntos Obtenidos', 'Driver': 'Piloto'},
    text_auto=True,
    color_discrete_map=colores_f1
)

st.plotly_chart(fig_sprint, use_container_width=True)

st.info("""
Nota cómo los resultados de las Sprint reflejan la superioridad 
mecánica de ciertos equipos en pistas específicas. Al no haber estrategia de neumáticos que salve 
a un auto lento, el formato Sprint premió la velocidad directa, marcando diferencias clave en la 
recta final del campeonato.
""")

# Mapa de Colores para Escuderías
colores_equipos = {
    'McLaren Mercedes': '#FF8000',           
    'Red Bull Racing Honda RBPT': "#0600B0", 
    'Mercedes': '#00D2BE',                   
    'Ferrari': '#DC0000',                    
    'Aston Martin Aramco Mercedes': '#229971', 
    'Haas Ferrari': '#B6BABD',               
    'Visa Cash App RB Honda RBPT': '#6692FF',
    'Kick Sauber Ferrari': "#00B303",
    'Williams Mercedes': "#00BBFF",
    'Alpine Renault': "#D205FA"
}

#Visualización 3: Campeonato de Constructores
st.header("3. La Caída del Imperio: Campeonato de Constructores")
st.markdown("""Esta visualización muestra el acumulado de puntos por equipo. Es aquí donde se observa 
el impacto real de tener dos pilotos sumando de forma constante frente a un liderato individual.""")

equipos_disponibles = team_cum.columns.drop('Track').tolist()

#Selector de equipos para comparar
equipos_seleccionados = st.multiselect(
    "Selecciona escuderías para comparar el dominio técnico:",
    options=equipos_disponibles,
    default=['McLaren Mercedes', 'Red Bull Racing Honda RBPT', 'Mercedes']
)

if equipos_seleccionados:
    fig_const = px.line(
        team_cum, 
        x='Track', 
        y=equipos_seleccionados,
        title="Evolución de Puntos por Constructor (Temporada 2025)",
        labels={'value': 'Puntos Totales Acumulados', 'Track': 'Gran Premio', 'variable': 'Escudería'},
        color_discrete_map=colores_equipos,
        markers=True 
    )
    
    fig_const.update_traces(line=dict(width=4), marker=dict(size=8))
    
    fig_const.update_layout(
        hovermode="x unified",
        legend_title_text='Escudería'
    )
    
    st.plotly_chart(fig_const, use_container_width=True)

# Conclusión Narrativa
st.divider()
st.header("🏁 Conclusión: El Triunfo del Colectivo sobre lo Individual")

st.markdown("""
Al inicio de este análisis planteamos una **pregunta de investigación**: *¿Fue la temporada 2025 el año del cambio de guardia definitivo en la Fórmula 1, donde el trabajo en equipo superó al talento individual?*

Los datos oficiales de la temporada nos permiten concluir con un rotundo **sí**. A través de nuestro recorrido visual, hemos desglosado la anatomía de este cambio de era:

* **En lo individual:** Max Verstappen demostró que sigue siendo un piloto de época, extrayendo el máximo de su monoplaza. Sin embargo, Lando Norris probó que, con el desarrollo correcto, el campeonato de pilotos ya no es intocable.
* **En el ritmo puro:** Las métricas de las carreras Sprint evidenciaron que la ventaja técnica absoluta que Red Bull mantuvo desde 2022 desapareció. La velocidad punta dejó de ser un monopolio, repartiéndose entre McLaren, Ferrari y Mercedes dependiendo del circuito.
* **En lo colectivo (El factor decisivo):** El gráfico del Campeonato de Constructores dictó la verdadera sentencia. Mientras Red Bull dependió abrumadoramente de los puntos generados por un solo piloto, McLaren construyó su campeonato sobre la consistencia dual y letal de Norris y Piastri. 

**El veredicto de los datos:** La temporada 2025 de Fórmula 1 pasará a la historia no solo como el año en que cayó el imperio de Red Bull, sino como una lección magistral de gestión deportiva. En la actual era de límite de presupuesto y regulaciones estrictas, los datos demuestran que **un equipo estructuralmente equilibrado siempre terminará superando a una sola estrella.**
""")

st.success("""
**Proyecto Final - Visualización Gráfica para IA** Elaborado por: Emilio Luevano Vazquez  
Universidad Iberoamericana León
""")