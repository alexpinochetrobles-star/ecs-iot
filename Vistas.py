from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .models import LecturaPozo, EventoBomba
from .services import gpio_service


@login_required
def dashboard(request):
    return render(request, "dashboard/dashboard.html")


@login_required
def api_ultimas_lecturas(request):
    lecturas = list(reversed(LecturaPozo.objects.all()[:60]))
    ultima = lecturas[-1] if lecturas else None
    return JsonResponse({
        "labels":          [l.fecha_hora.strftime("%H:%M:%S") for l in lecturas],
        "nivel_estatico":  [l.nivel_estatico_m for l in lecturas],
        "nivel_dinamico":  [l.nivel_dinamico_m for l in lecturas],
        "caudal":          [l.caudal_lps for l in lecturas],
        "ultima": {
            "nivel_estatico_m": ultima.nivel_estatico_m if ultima else 0,
            "nivel_dinamico_m": ultima.nivel_dinamico_m if ultima else 0,
            "caudal_lps":       ultima.caudal_lps       if ultima else 0,
            "fecha_hora":       ultima.fecha_hora.strftime("%H:%M:%S") if ultima else "--",
        },
    })


@login_required
def api_estado_gpio(request):
    return JsonResponse({
        "bomba_encendida":         gpio_service.estado_bomba(),
        "nivel_minimo_ok":         gpio_service.nivel_minimo_ok(),
        "paro_emergencia_activo":  gpio_service.paro_emergencia_activo(),
    })


@login_required
@permission_required("dashboard.can_control_bomba", raise_exception=True)
@require_POST
def api_controlar_bomba(request):
    accion = request.POST.get("accion")
    if accion == "on":
        ok, msg = gpio_service.encender_bomba()
        tipo = "ENCENDIDO" if ok else "BLOQUEO"
    elif accion == "off":
        ok, msg = gpio_service.apagar_bomba()
        tipo = "APAGADO"
    else:
        return JsonResponse({"ok": False, "mensaje": "Acción inválida"}, status=400)

    EventoBomba.objects.create(tipo=tipo, usuario=request.user.username, descripcion=msg)
    return JsonResponse({"ok": ok, "mensaje": msg})