from flask import Flask, render_template_string, request, jsonify
import paho.mqtt.client as mqtt
import threading

app = Flask(__name__)

# Configuración MQTT (ajusta con tus credenciales)
MQTT_BROKER = "serveo.net"  # o tu URL de Cloudflare
MQTT_PORT = 8080 #1883
MQTT_USER = "esp8266test"
MQTT_PASS = "hola123"
TOPIC_CONTROL = "casa/ventilador/control"
TOPIC_TEMP = "casa/sensor/temperatura"
TOPIC_HUM = "casa/sensor/humedad"

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)


# Estado inicial
current_state = {
    'ventilador': 'off',
    'temperatura': 0.0,
    'humedad': 0.0
}

# HTML Template (puedes moverlo a un archivo .html aparte)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Control Ventilador</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .card { 
            border: 1px solid #ddd; 
            border-radius: 8px; 
            padding: 20px; 
            margin: 10px; 
            display: inline-block;
            width: 200px;
            text-align: center;
        }
        button { 
            padding: 10px 15px; 
            margin: 5px; 
            cursor: pointer; 
            font-size: 16px;
        }
        .on { background-color: #4CAF50; color: white; }
        .off { background-color: #f44336; color: white; }
    </style>
</head>
<body>
    <h1>Control de Ventilador</h1>
    
    <div class="card">
        <h2>Temperatura</h2>
        <div id="temp">{{ temp }} °C</div>
    </div>
    
    <div class="card">
        <h2>Humedad</h2>
        <div id="hum">{{ hum }} %</div>
    </div>
    
    <div class="card">
        <h2>Ventilador</h2>
        <button onclick="control('on')" class="on">ENCENDER</button>
        <button onclick="control('off')" class="off">APAGAR</button>
        <p>Estado actual: <span id="state">{{ fan }}</span></p>
    </div>

    <script>
        function control(estado) {
            fetch('/ventilador/' + estado, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('state').textContent = data.estado;
                });
        }

        // Actualización en tiempo real (cada 3 segundos)
        setInterval(() => {
            fetch('/datos')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('temp').textContent = data.temperatura + ' °C';
                    document.getElementById('hum').textContent = data.humedad + ' %';
                    document.getElementById('state').textContent = data.ventilador;
                });
        }, 3000);
    </script>
</body>
</html>
"""

# Callback MQTT para recibir datos
def on_message(client, userdata, msg):
    try:
        if msg.topic == TOPIC_TEMP:
            current_state['temperatura'] = float(msg.payload.decode())
        elif msg.topic == TOPIC_HUM:
            current_state['humedad'] = float(msg.payload.decode())
    except Exception as e:
        print("Error procesando mensaje:", e)

# Conectar MQTT (sin threads)
try:
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.subscribe("casa/sensor/#")
    mqtt_client.loop_start()  # Usa loop_start() en lugar de threading PARA COGER LOS VALORES
except Exception as e:
    print("Error MQTT:", str(e))



# Rutas Flask
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, 
                               temp=current_state['temperatura'],
                               hum=current_state['humedad'],
                               fan=current_state['ventilador'])

@app.route('/ventilador/<estado>', methods=['POST'])
def control_ventilador(estado):
    if estado in ['on', 'off']:
        current_state['ventilador'] = estado
        # Publicar comando MQTT
        mqtt_client.publish(TOPIC_CONTROL, estado)
        return jsonify({"status": "success", "estado": estado})
    return jsonify({"status": "error"})

@app.route('/datos')
def datos():
    return jsonify(current_state)

if __name__ == '__main__':
    # Iniciar hilo MQTT
    #threading.Thread(target=mqtt_thread, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=True)