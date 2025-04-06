from flask import Flask, request, jsonify
import requests  # Para hacer HTTP al ESP8266

app = Flask(__name__)

# Base de datos "falsa" para almacenar datos
sensor_data = {"temp": 0, "hume": 0}
esp8266_ip = "192.168.18.79"  # Cambia por la IP del ESP

@app.route("/")
def home():
    return f"""
    <h1>Control ESP8266 desde Flask</h1>
    <p>Temperatura: {sensor_data['temp']}°C</p>
    <p>Humedad: {sensor_data['hume']}% </p>
    <p>
        <button onclick="controlVentilador('on')"> Encender Ventilador</button>
        <button onclick="controlVentilador('off')"> Apagar Ventilador</button>
    </p>
    <script>
        function controlVentilador(state) {{
            fetch(`/control-ventilador/${{state}}`)
                .then(response => alert(response.ok ? "Éxito" : "Error"));
        }}
    </script>
    """

@app.route("/update-sensors", methods=["POST"])
def update_sensors():
    sensor_data["temp"] = float(request.form.get("temp"))
    sensor_data["hume"] = float(request.form.get("hume"))

    return jsonify({"status": "success"})

@app.route("/control-ventilador/<state>")
def control_ventilador(state):
    try:
        # Envía comando al ESP8266
        response = requests.get(f"http://{esp8266_ip}/ventilador?state={state}")
        return response.text  # "ventilador ON" o "LED OFF"
    except:
        return "Error comunicándose con el ESP8266", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)