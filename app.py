import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

st.set_page_config(page_title="AirSense - Monitor de Qualidade do Ar", layout="centered")
st.title("🌍 AirSense - Monitor de Qualidade do Ar")

# Input do usuário
localizacao = st.text_input("Digite sua cidade, bairro ou local (ex: 'Hospital Albert Einstein, Morumbi, SP'):")

if localizacao:
    geolocator = Nominatim(user_agent="airsense-app")
    
    try:
        location = geolocator.geocode(localizacao, timeout=5)
    except (GeocoderTimedOut, GeocoderUnavailable):
        location = None

    if location is None:
        st.error("Localização não encontrada ou tempo limite excedido. Tente ser mais específico ou aguarde um momento e tente novamente.")
        st.stop()

    latitude = location.latitude
    longitude = location.longitude

    st.success(f"📍 Localização encontrada: {location.address}")

    # Mostrar mapa com localização
    st.markdown("### 🗺️ Localização no Mapa")
    m = folium.Map(location=[latitude, longitude], zoom_start=13)
    folium.Marker([latitude, longitude], tooltip="Você está aqui").add_to(m)
    st_folium(m, width=700, height=400)

    # Chave da API do OpenWeather
    api_key = st.secrets["OPENWEATHER_API_KEY"]

    # Qualidade do ar
    air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={latitude}&lon={longitude}&appid={api_key}"
    air_response = requests.get(air_url)

    # Clima atual
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric&lang=pt_br"
    weather_response = requests.get(weather_url)

    st.markdown("### 🌦️ Condições Climáticas")
    if weather_response.status_code == 200:
        clima = weather_response.json()
        temperatura = clima["main"]["temp"]
        umidade = clima["main"]["humidity"]
        vento = clima["wind"]["speed"]
        descricao = clima["weather"][0]["description"].capitalize()

        st.metric("🌡️ Temperatura", f"{temperatura} °C")
        st.metric("💧 Umidade", f"{umidade}%")
        st.metric("🌬️ Vento", f"{vento} m/s")
        st.markdown(f"**Descrição:** {descricao}")
    else:
        st.warning("Não foi possível obter os dados do clima.")

    st.markdown("### 📊 Qualidade do Ar (AQI)")
    if air_response.status_code == 200:
        dados_ar = air_response.json()
        aqi = dados_ar['list'][0]['main']['aqi']

        if aqi == 1:
            st.success("✅ Qualidade do ar: Boa")
        elif aqi == 2:
            st.info("ℹ️ Qualidade do ar: Razoável")
        elif aqi == 3:
            st.warning("⚠️ Qualidade do ar: Moderada")
        elif aqi == 4:
            st.error("🚨 Qualidade do ar: Ruim. Evite atividades ao ar livre!")
        elif aqi == 5:
            st.error("⛔ Qualidade do ar: Muito ruim. Permaneça em locais fechados sempre que possível!")
    else:
        st.warning("Não foi possível obter os dados da qualidade do ar.")

else:
    st.error("📍 Localização não encontrada. Tente inserir um endereço mais específico.")
