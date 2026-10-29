"""Servicio de control de GPIO de la Raspberry Pi (rol de PLC)."""
import RPi.GPIO as GPIO
from threading import Lock

# Numeración BCM
PIN_RELE_BOMBA      = 27   # Salida -> relé de la bomba
PIN_FLOTADOR_MIN    = 17   # Entrada -> flotador de nivel mínimo (contacto NC)
PIN_PARO_EMERGENCIA = 22   # Entrada -> pulsador de paro NC

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(PIN_RELE_BOMBA,      GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(PIN_FLOTADOR_MIN,    GPIO.IN,  pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_PARO_EMERGENCIA, GPIO.IN,  pull_up_down=GPIO.PUD_UP)

_lock = Lock()


def nivel_minimo_ok() -> bool:
    """Flotador normalmente cerrado: LOW = nivel OK."""
    return GPIO.input(PIN_FLOTADOR_MIN) == GPIO.LOW


def paro_emergencia_activo() -> bool:
    """Botón NC: HIGH significa que fue presionado."""
    return GPIO.input(PIN_PARO_EMERGENCIA) == GPIO.HIGH


def estado_bomba() -> bool:
    return GPIO.input(PIN_RELE_BOMBA) == GPIO.HIGH


def encender_bomba():
    with _lock:
        if not nivel_minimo_ok():
            return False, "BLOQUEO: nivel mínimo alcanzado (protección de bomba)"
        if paro_emergencia_activo():
            return False, "BLOQUEO: paro de emergencia activo"
        GPIO.output(PIN_RELE_BOMBA, GPIO.HIGH)
        return True, "Bomba encendida"


def apagar_bomba():
    with _lock:
        GPIO.output(PIN_RELE_BOMBA, GPIO.LOW)
        return True, "Bomba apagada"


def cleanup():
    try:
        GPIO.cleanup()
    except Exception:
        pass