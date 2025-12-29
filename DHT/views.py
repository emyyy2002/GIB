from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils.safestring import mark_safe
from .models import Dht11
import json
import csv


# ---------- DASHBOARD ----------
def dashboard(request):
    # page avec les 2 cartes (temp & humidité)
    return render(request, "dashboard.html")


# ---------- /latest/ ----------
def latest_json(request):
    last = Dht11.objects.order_by("-dt").first()  # Changé: "-dt" au lieu de "-created_at"
    if not last:
        return JsonResponse({"temp": None, "hum": None, "date": None})

    return JsonResponse({
        "temp": float(last.temp),       # Changé: last.temp au lieu de last.temperature
        "hum": float(last.hum),         # Changé: last.hum au lieu de last.humidity
        "date": last.dt.isoformat() if last.dt else None,  # Changé: last.dt
    })


# ---------- HISTORIQUE TEMPÉRATURE ----------
def temperature_history(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    qs = Dht11.objects.all().order_by("dt")  # Changé: "dt" au lieu de "created_at"
    if start_date:
        qs = qs.filter(dt__date__gte=start_date)  # Changé: dt__date
    if end_date:
        qs = qs.filter(dt__date__lte=end_date)    # Changé: dt__date

    labels = [m.dt.strftime("%Y-%m-%d %H:%M") if m.dt else "" for m in qs]  # Changé: m.dt
    temps = [float(m.temp) if m.temp is not None else 0 for m in qs]        # Changé: m.temp
    hums = [float(m.hum) if m.hum is not None else 0 for m in qs]           # Changé: m.hum

    context = {
        "labels": mark_safe(json.dumps(labels)),
        "temps": mark_safe(json.dumps(temps)),
        "hums": mark_safe(json.dumps(hums)),
        "start_date": start_date or "",
        "end_date": end_date or "",
    }
    return render(request, "temperature_history.html", context)


def temperature_history_csv(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    qs = Dht11.objects.all().order_by("dt")  # Changé: "dt"
    if start_date:
        qs = qs.filter(dt__date__gte=start_date)  # Changé: dt__date
    if end_date:
        qs = qs.filter(dt__date__lte=end_date)    # Changé: dt__date

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="temperature_history.csv"'

    writer = csv.writer(response)
    writer.writerow(["Date", "Température (°C)", "Humidité (%)"])  # Retiré: Capteur
    for m in qs:
        writer.writerow([
            m.dt if m.dt else "",            # Changé: m.dt
            m.temp if m.temp is not None else "",  # Changé: m.temp
            m.hum if m.hum is not None else ""     # Changé: m.hum
        ])

    return response


# ---------- HISTORIQUE HUMIDITÉ ----------
def humidity_history(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    qs = Dht11.objects.all().order_by("dt")  # Changé: "dt"
    if start_date:
        qs = qs.filter(dt__date__gte=start_date)  # Changé: dt__date
    if end_date:
        qs = qs.filter(dt__date__lte=end_date)    # Changé: dt__date

    # ⚠️ important : ISO 8601 pour l'axe temps
    labels = [m.dt.isoformat() if m.dt else "" for m in qs]  # Changé: m.dt
    temps = [float(m.temp) if m.temp is not None else 0 for m in qs]  # Changé: m.temp
    hums = [float(m.hum) if m.hum is not None else 0 for m in qs]     # Changé: m.hum

    context = {
        "labels": mark_safe(json.dumps(labels)),
        "temps": mark_safe(json.dumps(temps)),
        "hums": mark_safe(json.dumps(hums)),
        "start_date": start_date or "",
        "end_date": end_date or "",
    }
    return render(request, "humidity_history.html", context)


def humidity_history_csv(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    qs = Dht11.objects.all().order_by("dt")  # Changé: "dt"
    if start_date:
        qs = qs.filter(dt__date__gte=start_date)  # Changé: dt__date
    if end_date:
        qs = qs.filter(dt__date__lte=end_date)    # Changé: dt__date

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="humidity_history.csv"'

    writer = csv.writer(response)
    writer.writerow(["Date", "Température (°C)", "Humidité (%)"])  # Retiré: Capteur
    for m in qs:
        writer.writerow([
            m.dt if m.dt else "",            # Changé: m.dt
            m.temp if m.temp is not None else "",  # Changé: m.temp
            m.hum if m.hum is not None else ""     # Changé: m.hum
        ])

    return response