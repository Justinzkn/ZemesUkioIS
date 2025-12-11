from datetime import date, datetime
import calendar

from django.shortcuts import render, redirect
from django.db import connection
from datetime import datetime
from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os
from django.conf import settings

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def grafikas_perziura(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/prisijungimas/")

    today = date.today()

    nuo_raw = request.GET.get("nuo") or ""
    iki_raw = request.GET.get("iki") or ""

    if not nuo_raw:
        nuo = today.replace(day=1)
    else:
        try:
            nuo = datetime.strptime(nuo_raw, "%Y-%m-%d").date()
        except ValueError:
            nuo = today.replace(day=1)

    if not iki_raw:
        paskutine_diena = calendar.monthrange(today.year, today.month)[1]
        iki = today.replace(day=paskutine_diena)
    else:
        try:
            iki = datetime.strptime(iki_raw, "%Y-%m-%d").date()
        except ValueError:
            paskutine_diena = calendar.monthrange(today.year, today.month)[1]
            iki = today.replace(day=paskutine_diena)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                Data,
                Darbas_nuo,
                Darbas_iki,
                Poilsis
            FROM grafikas
            WHERE fk_Naudotojas_id_Naudotojas = %s
              AND Data BETWEEN %s AND %s
            ORDER BY Data
        """, [user_id, nuo, iki])
        dienos = dictfetchall(cursor)

    return render(request, "grafikai.html", {
        "dienos": dienos,
        "nuo": nuo.isoformat(),
        "iki": iki.isoformat(),
    })


# ----------------------------------------------------------
# Nauja grafiko keitimo užklausa + savo užklausų sąrašas
# ----------------------------------------------------------
def grafiko_uzklausa_nauja(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/prisijungimas/")

    msg = None
    msg_type = "info"
    today_str = date.today().isoformat()

    if request.method == "POST":
        data_raw = (request.POST.get("data") or "").strip()
        tipas = (request.POST.get("tipas") or "darbas").strip()  # darbas / poilsis
        darbas_nuo_raw = (request.POST.get("darbas_nuo") or "").strip()
        darbas_iki_raw = (request.POST.get("darbas_iki") or "").strip()
        priezastis = (request.POST.get("priezastis") or "").strip()

        # --- DATA ---
        if not data_raw:
            msg = "Pasirinkite datą."
            msg_type = "error"
        else:
            try:
                data_val = datetime.strptime(data_raw, "%Y-%m-%d").date()
            except ValueError:
                msg = "Neteisingas datos formatas."
                msg_type = "error"

        # --- Tipas / laikas ---
        poilsis = 1 if tipas == "poilsis" else 0
        darbas_nuo = None
        darbas_iki = None

        if msg is None and not poilsis:
            # darbo diena – privalomi laikai
            if not darbas_nuo_raw or not darbas_iki_raw:
                msg = "Nurodykite darbo pradžios ir pabaigos laiką."
                msg_type = "error"
            else:
                try:
                    datetime.strptime(darbas_nuo_raw, "%H:%M")
                    datetime.strptime(darbas_iki_raw, "%H:%M")
                    darbas_nuo = darbas_nuo_raw
                    darbas_iki = darbas_iki_raw
                except ValueError:
                    msg = "Neteisingas laiko formatas (naudokite HH:MM)."
                    msg_type = "error"

        if msg is None and not priezastis:
            priezastis = None

        # --- ĮRAŠOM UŽKLAUSĄ ---
        if msg is None:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO grafiko_uzklausa
                      (Data, Darbas_nuo, Darbas_iki, Poilsis,
                       Priezastis, Busena, fk_Naudotojas_id_Naudotojas)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, [data_val, darbas_nuo, darbas_iki, poilsis,
                      priezastis, 0, user_id])

            return redirect("/grafikai/uzklausa/?success=1")

    # GET dalis: sėkmės flagas + savo užklausų sąrašas
    success = request.GET.get("success") == "1"

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                id_Grafiko_uzklausa,
                Data,
                Darbas_nuo,
                Darbas_iki,
                Poilsis,
                Priezastis,
                Busena
            FROM grafiko_uzklausa
            WHERE fk_Naudotojas_id_Naudotojas = %s
            ORDER BY Data DESC, id_Grafiko_uzklausa DESC
        """, [user_id])
        uzklausos = dictfetchall(cursor)

    return render(request, "grafiko_keitimo_uzklausa.html", {
        "msg": msg,
        "msg_type": msg_type,
        "success": success,
        "today": today_str,
        "uzklausos": uzklausos,
    })


def uzklausos_sarasas(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/prisijungimas/")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                id_Uzklausa,
                Uzklausos_tipas,
                Priezastis,
                Data,
                Naujas_pradzios_laikas,
                Naujas_pabaigos_laikas
            FROM uzklausa
            WHERE fk_Naudotojas_id_Naudotojas = %s
            ORDER BY Data DESC, id_Uzklausa DESC
        """, [user_id])
        uzklausos = dictfetchall(cursor)

    return render(request, "uzklausu_sarasas.html", {
        "uzklausos": uzklausos,
    })

def uzklausa_istrinti(request, id):
    """
    Paprastos užklausos trynimas.
    - galima trinti tik savo užklausą
    - būsenos lauko nebeturime, todėl jei užklausa egzistuoja ir priklauso
      naudotojui, ją tiesiog šaliname.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/prisijungimas/")

    if request.method != "POST":
        return redirect("/grafikai/uzklausos/")

    with connection.cursor() as cursor:
        # pažiūrim, ar tokia užklausa yra ir kam ji priklauso
        cursor.execute("""
            SELECT fk_Naudotojas_id_Naudotojas
            FROM uzklausa
            WHERE id_Uzklausa = %s
        """, [id])
        row = cursor.fetchone()

        if not row:
            # nėra tokios užklausos – tyliai grįžtam
            return redirect("/grafikai/uzklausos/")

        owner_id = row[0]

        # ne šio naudotojo užklausa – trinti negalima
        if owner_id != user_id:
            return redirect("/grafikai/uzklausos/")

        # viskas ok – šalinam
        cursor.execute("""
            DELETE FROM uzklausa
            WHERE id_Uzklausa = %s
        """, [id])

    return redirect("/grafikai/uzklausos/?deleted=1")

def uzklausa_nauja(request):
    """
    Paprastos užklausos (atostogų, biuletenio ir pan.) kūrimas.
    Įrašo į lentelę `uzklausa`.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/prisijungimas/")

    msg = None
    msg_type = "info"

    if request.method == "POST":
        tipas = (request.POST.get("uzklausos_tipas") or "").strip()
        priezastis = (request.POST.get("priezastis") or "").strip()

        nuo_data = (request.POST.get("nuo_data") or "").strip()
        iki_data = (request.POST.get("iki_data") or "").strip()
        nuo_laikas = (request.POST.get("nuo_laikas") or "").strip()
        iki_laikas = (request.POST.get("iki_laikas") or "").strip()

        # bazinė validacija
        if not tipas or not priezastis or not nuo_data or not iki_data:
            msg = "Užpildykite visus privalomus laukus."
            msg_type = "error"
        else:
            # datos validacija
            try:
                nuo_dt = datetime.strptime(nuo_data, "%Y-%m-%d")
                iki_dt = datetime.strptime(iki_data, "%Y-%m-%d")
            except ValueError:
                msg = "Neteisingas datos formatas."
                msg_type = "error"
            else:
                if iki_dt < nuo_dt:
                    msg = "'Iki' data negali būti ankstesnė už 'Nuo' datą."
                    msg_type = "error"
                else:
                    # jei laikas neįvestas – laikom 00:00
                    if not nuo_laikas:
                        nuo_laikas = "00:00"
                    if not iki_laikas:
                        iki_laikas = "00:00"

                    # sudedam į DATETIME stringus DB laukams
                    nuo_full = f"{nuo_data} {nuo_laikas}:00"
                    iki_full = f"{iki_data} {iki_laikas}:00"

                    today = date.today()

                    with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO uzklausa
                              (Uzklausos_tipas,
                               Priezastis,
                               Data,
                               Naujas_pradzios_laikas,
                               Naujas_pabaigos_laikas,
                               fk_Naudotojas_id_Naudotojas)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, [
                            tipas,
                            priezastis,
                            today,
                            nuo_full,
                            iki_full,
                            user_id
                        ])

                    # sėkmė – grįžtam į sąrašą
                    return redirect("/grafikai/uzklausos/")

    return render(request, "nauja_uzklausa.html", {
        "msg": msg,
        "msg_type": msg_type,
    })

def algalapis_generuoti(request):
    """
    Algalapio generavimo langas:
    - GET  -> forma su laikotarpiu
    - POST -> validuojam datas, suskaičiuojam valandas ir sugeneruojam PDF
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/prisijungimas/")

    msg = None

    if request.method == "POST":
        nuo_raw = (request.POST.get("nuo") or "").strip()
        iki_raw = (request.POST.get("iki") or "").strip()

        # --- datos validacija ---
        try:
            nuo = datetime.strptime(nuo_raw, "%Y-%m-%d").date()
            iki = datetime.strptime(iki_raw, "%Y-%m-%d").date()
        except ValueError:
            msg = "Neteisingas datos formatas."
        else:
            if nuo > iki:
                msg = "'Nuo' data negali būti vėlesnė už 'Iki' datą."
            else:
                # --- pasiimam grafiko įrašus pasirinktam laikotarpiui ---
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT Data, Darbas_Nuo, Darbas_Iki
                        FROM grafikas
                        WHERE fk_Naudotojas_id_Naudotojas = %s
                          AND Data BETWEEN %s AND %s
                        ORDER BY Data, Darbas_Nuo
                    """, [user_id, nuo, iki])
                    rows = cursor.fetchall()

                if not rows:
                    msg = "Pasirinktam laikotarpiui nėra darbo grafiko įrašų."
                else:
                    total_hours = 0.0

                    for d, start_t, end_t in rows:
                        # jeigu laikas neužpildytas – praleidžiam eilutę
                        if start_t is None or end_t is None:
                            continue

                        start_dt = datetime.combine(d, start_t)
                        end_dt = datetime.combine(d, end_t)

                        diff_h = (end_dt - start_dt).total_seconds() / 3600.0
                        if diff_h > 0:
                            total_hours += diff_h

                    if total_hours == 0:
                        msg = "Pasirinktam laikotarpiui nerasta pilnai suvestų darbo valandų."
                    else:
                        # supaprastintas skaičiavimas
                        hourly_rate = 10.00  # € už valandą
                        bruto = round(total_hours * hourly_rate, 2)
                        taxes = round(bruto * 0.2, 2)   # 20 % mokesčiai
                        neto = round(bruto - taxes, 2)

                        font_path = os.path.join(
                            settings.BASE_DIR,
                            "venv",
                            "lib",
                            "site-packages",
                            "reportlab",
                            "fonts",
                            "DejaVuSans.ttf",
                        )
                        pdfmetrics.registerFont(TTFont("DejaVu", font_path))

                        # --- generuojam PDF su reportlab ---
                        buffer = BytesIO()
                        p = canvas.Canvas(buffer, pagesize=A4)
                        width, height = A4
                        y = height - 50

                        p.setFont("DejaVu", 16)
                        p.drawString(50, y, "Algalapis")
                        y -= 30

                        p.setFont("DejaVu", 11)
                        p.drawString(50, y, f"Laikotarpis: {nuo} – {iki}")
                        y -= 18
                        p.drawString(50, y, f"Bendras dirbtų valandų sk.: {total_hours:.2f}")
                        y -= 18
                        p.drawString(50, y, f"Valandinis atlygis: {hourly_rate:.2f} €")
                        y -= 18
                        p.drawString(50, y, f"Bruto suma: {bruto:.2f} €")
                        y -= 18
                        p.drawString(50, y, f"Numatomi mokesčiai (20 %): {taxes:.2f} €")
                        y -= 18
                        p.drawString(50, y, f"Neto suma: {neto:.2f} €")

                        p.showPage()
                        p.save()

                        pdf = buffer.getvalue()
                        buffer.close()

                        filename = f"algalapis_{nuo}_{iki}.pdf"
                        response = HttpResponse(pdf, content_type="application/pdf")
                        response["Content-Disposition"] = f'attachment; filename=\"{filename}\"'
                        return response

    # GET arba klaidos atveju – rodome formą
    return render(request, "algalapis.html", {
        "msg": msg,
    })