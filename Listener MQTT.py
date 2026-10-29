import json
import os
import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from dashboard.models import LecturaPozo, EventoBomba
from dashboard.services import gpio_service

TOPIC_LECTURAS = "pozo/profundidad/lecturas"
NIVEL_CRITICO_M = 60.0        # Ajusta según tu pozo
NIVEL_APAGADO_M = 55.0        # Apagado automático cuando la bomba succiona


class Command(BaseCommand):
    help = "Escucha MQTT del ESP32, guarda lecturas y controla alarmas"

    def handle(self, *args, **opts):
        host = os.environ.get("MQTT_HOST", "mosquitto")
        port = int(os.environ.get("MQTT_PORT", 1883))
        user = os.environ.get("MQTT_USERNAME", "ecs")
        pwd  = os.environ.get("MQTT_PASSWORD", "")

        def on_connect(client, _u, _f, rc):
            if rc == 0:
                client.subscribe(TOPIC_LECTURAS, qos=1)
                self.stdout.write(self.style.SUCCESS("Conectado a MQTT"))
            else:
                self.stdout.write(self.style.ERROR(f"MQTT rc={rc}"))

        def on_message(client, _u, msg):
            try:
                payload = json.loads(msg.payload.decode())
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"JSON inválido: {e}"))
                return

            nivel   = float(payload.get("nivel_m", 0.0))
            caudal  = float(payload.get("caudal_lps", 0.0))
            ne      = float(payload.get("nivel_estatico_m", nivel))
            nd      = float(payload.get("nivel_dinamico_m", nivel))
            bomba   = gpio_service.estado_bomba()

            LecturaPozo.objects.create(
                nivel_estatico_m=ne,
                nivel_dinamico_m=nd,
                caudal_lps=caudal,
                bomba_encendida=bomba,
            )
            self.stdout.write(
                f"NE={ne}m ND={nd}m Q={caudal}L/s Bomba={'ON' if bomba else 'OFF'}"
            )

            # Apagado automático por nivel crítico
            if bomba and nivel >= NIVEL_APAGADO_M:
                ok, msg_txt = gpio_service.apagar_bomba()
                EventoBomba.objects.create(
                    tipo="AUTO_APAGADO",
                    usuario="sistema",
                    descripcion=f"Nivel crítico {nivel:.2f}m >= {NIVEL_APAGADO_M}m: {msg_txt}",
                )
                self.stdout.write(self.style.WARNING(f"⚠️ {msg_txt}"))

        client = mqtt.Client()
        client.username_pw_set(user, pwd)
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(host, port, 60)
        client.loop_forever()