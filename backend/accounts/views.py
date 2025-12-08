from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError, connection
from .models import Naudotojas
import hashlib

def registracija(request):
    if request.method == "POST":
        vardas = request.POST.get("Vardas")
        pavarde = request.POST.get("Pavarde")
        email = request.POST.get("El_pastas")
        slaptazodis = request.POST.get("Slaptazodis")
        pareigos = request.POST.get("Pareigos")
        saskaita = request.POST.get("Saskaitos_numeris")

        try:
            Naudotojas.objects.create(
                Vardas=vardas,
                Pavarde=pavarde,
                El_pastas=email,
                Slaptazodis=slaptazodis,
                Pareigos=pareigos,
                Saskaitos_numeris=saskaita
            )
            messages.success(request, "Registracija sėkminga!")
            return redirect("/prisijungimas/")  # kol kas gali būti tuščias puslapis
        except IntegrityError:
            messages.error(request, "Toks el. paštas jau naudojamas!")

    return render(request, "registracija.html")


def prisijungimas(request):
    if request.method == "POST":
        el_pastas = request.POST.get("El_pastas")
        slaptazodis = request.POST.get("Slaptazodis")

        cursor = connection.cursor()
        cursor.execute("""
            SELECT id_Naudotojas, Pareigos
            FROM naudotojas
            WHERE El_pastas = %s AND Slaptazodis = %s
        """, [el_pastas, slaptazodis])

        user = cursor.fetchone()

        if user:
            user_id, pareigos = user

            # SAUGOME SESIJOJE
            request.session["user_id"] = user_id
            request.session["pareigos"] = pareigos  # 1 = klientas, 2 = darbuotojas

            return redirect("/pagrindinis/")
        else:
            return render(request, "prisijungimas.html", {"error": "Neteisingi duomenys."})

    return render(request, "prisijungimas.html")



def atsijungti(request):
    request.session.flush()
    return redirect("/pagrindinis/")