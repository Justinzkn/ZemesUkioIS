from django.shortcuts import render, redirect
from django.db import connection
from datetime import date

# ------------------------------
# ĮRANGOS SĄRAŠAS
# ------------------------------
def irangos_perziura(request):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM iranga")
    iranga = cursor.fetchall()

    return render(request, "irangos_perziura.html", {"iranga": iranga})
# ------------------------------
# PRIDĖTI ĮRANGĄ
# ------------------------------
def iranga_prideti(request):

    if request.method == "POST":
        pavad = request.POST.get("Pavadinimas")
        tipas = request.POST.get("Tipas")
        bukle = request.POST.get("Bukle")
        vieta = request.POST.get("Vieta")
        verte = request.POST.get("Verte")
        gamintojas = request.POST.get("Gamintojas")
        pag_data = request.POST.get("Pagaminimo_data")
        tech = request.POST.get("Technine_apziura")

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO iranga (Pavadinimas, Tipas, Bukle, Vieta, Verte, Gamintojas, Pagaminimo_data, Technine_apziura)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, [pavad, tipas, bukle, vieta, verte, gamintojas, pag_data, tech])

        return redirect('/iranga/')

    return render(request, "iranga_prideti.html")

# ------------------------------
# REDAGAVIMAS
# ------------------------------
def iranga_redaguoti(request, id):

    if request.method == "POST":
        print("POST DATA:", request.POST)

        pavad = request.POST.get("Pavadinimas")
        tipas = request.POST.get("Tipas")
        bukle = request.POST.get("Bukle")
        vieta = request.POST.get("Vieta")
        verte = request.POST.get("Verte")
        gamintojas = request.POST.get("Gamintojas")
        pag_data = request.POST.get("Pagaminimo_data")
        tech = request.POST.get("Technine_apziura")

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE iranga 
                SET 
                    Pavadinimas=%s, 
                    Tipas=%s, 
                    Bukle=%s, 
                    Vieta=%s, 
                    Verte=%s, 
                    Gamintojas=%s, 
                    Pagaminimo_data=%s, 
                    Technine_apziura=%s 
                WHERE id_iranga=%s
            """, [pavad, tipas, bukle, vieta, verte, gamintojas, pag_data, tech, id])

        return redirect('/iranga/')

    # GET – gauti senus duomenis
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM iranga WHERE id_iranga=%s", [id])
        ir = dictfetchone(cursor)

    return render(request, "iranga_redaguoti.html", {"iranga": ir})

# ------------------------------
# ŠALINIMAS
# ------------------------------
def iranga_salinti(request, id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM iranga WHERE id_iranga=%s", [id])

    return redirect('/iranga/')

# ------------------------------
# KOMPLEKTAVIMAS (dummy)
# ------------------------------
def _komplektavimo_kontekstas(error=None):
    """Pagalbinė funkcija – vienoje vietoje surenkam visus duomenis šablonui."""
    with connection.cursor() as cursor:
        # traktoriai (Tipas = 1) ir dar niekur nenaudojami
        cursor.execute("""
            SELECT i.*
            FROM iranga i
            WHERE i.Tipas = 1
              AND (
                    (SELECT COUNT(*) FROM irangos_komplektas k
                     WHERE k.fk_Iranga_id_iranga = i.id_iranga)
                  + (SELECT COUNT(*) FROM irangos_komplekto_detale d
                     WHERE d.fk_iranga = i.id_iranga)
              ) = 0
            ORDER BY i.Pavadinimas
        """)
        traktoriai = dictfetchall(cursor)

        # agregatai (visi kiti tipai) ir dar niekur nenaudojami
        cursor.execute("""
            SELECT i.*
            FROM iranga i
            WHERE i.Tipas <> 1
              AND (
                    (SELECT COUNT(*) FROM irangos_komplektas k
                     WHERE k.fk_Iranga_id_iranga = i.id_iranga)
                  + (SELECT COUNT(*) FROM irangos_komplekto_detale d
                     WHERE d.fk_iranga = i.id_iranga)
              ) = 0
            ORDER BY i.Pavadinimas
        """)
        agregatai = dictfetchall(cursor)

        # darbuotojai (Pareigos = 2)
        cursor.execute("""
            SELECT id_Naudotojas, Vardas, Pavarde
            FROM naudotojas
            WHERE Pareigos = 2
            ORDER BY Pavarde, Vardas
        """)
        darbuotojai = dictfetchall(cursor)

        # esami komplektai (pagrindinė info)
        cursor.execute("""
            SELECT 
              k.id_Irangos_komplektas,
              k.Pavadinimas,
              k.Paskirtis,
              k.Sudarymo_data,
              t.Pavadinimas AS traktorius,
              n.Vardas,
              n.Pavarde
            FROM irangos_komplektas k
              LEFT JOIN iranga t ON t.id_iranga = k.fk_Iranga_id_iranga
              LEFT JOIN naudotojas n ON n.id_Naudotojas = k.fk_Naudotojas_id_Naudotojas
            ORDER BY k.id_Irangos_komplektas DESC
        """)
        komplektai = dictfetchall(cursor)

        # agregatai komplektuose
        cursor.execute("""
            SELECT d.fk_komplektas, i.Pavadinimas
            FROM irangos_komplekto_detale d
            JOIN iranga i ON i.id_iranga = d.fk_iranga
            ORDER BY i.Pavadinimas
        """)
        detales = dictfetchall(cursor)

    # sugrupuoju agregatus pagal komplekto ID
    agregatu_zemelapis = {}
    for row in detales:
        agregatu_zemelapis.setdefault(row["fk_komplektas"], []).append(row["Pavadinimas"])

    for k in komplektai:
        k["agregatai"] = ", ".join(agregatu_zemelapis.get(k["id_Irangos_komplektas"], [])) or "–"

    return {
        "traktoriai": traktoriai,
        "agregatai": agregatai,
        "darbuotojai": darbuotojai,
        "komplektai": komplektai,
        "error": error,
    }


def iranga_komplektavimas(request):
    if request.method == "POST":
        pavadinimas = request.POST.get("Pavadinimas")
        aprasymas = request.POST.get("Aprasymas")
        paskirtis = request.POST.get("Paskirtis")
        traktorius_id = request.POST.get("Traktorius")
        darbuotojas_id = request.POST.get("Darbuotojas")
        agregatai_ids = request.POST.getlist("Agregatai")

        # minimalus validavimas
        if not traktorius_id or not agregatai_ids:
            ctx = _komplektavimo_kontekstas(
                "Pasirinkite traktorių ir bent vieną agregatą."
            )
            return render(request, "iranga_komplektavimas.html", ctx)

        with connection.cursor() as cursor:
            # traktoriaus vieta
            cursor.execute("SELECT Vieta FROM iranga WHERE id_iranga=%s", [traktorius_id])
            row = cursor.fetchone()
            if not row:
                ctx = _komplektavimo_kontekstas("Pasirinktas traktorius nerastas.")
                return render(request, "iranga_komplektavimas.html", ctx)
            trakt_vieta = row[0]

            # traktorius jau komplekte?
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM irangos_komplektas WHERE fk_Iranga_id_iranga=%s)
                  + (SELECT COUNT(*) FROM irangos_komplekto_detale WHERE fk_iranga=%s)
            """, [traktorius_id, traktorius_id])
            if cursor.fetchone()[0] > 0:
                ctx = _komplektavimo_kontekstas("Šis traktorius jau priklauso kitam komplektui.")
                return render(request, "iranga_komplektavimas.html", ctx)

            # tikrinam kiekvieną agregatą
            for ag_id in agregatai_ids:
                # vieta
                cursor.execute("SELECT Vieta FROM iranga WHERE id_iranga=%s", [ag_id])
                row = cursor.fetchone()
                if not row:
                    ctx = _komplektavimo_kontekstas("Vienas iš agregatų nerastas.")
                    return render(request, "iranga_komplektavimas.html", ctx)
                ag_vieta = row[0]
                if ag_vieta != trakt_vieta:
                    ctx = _komplektavimo_kontekstas(
                        f"Agregato vieta ({ag_vieta}) nesutampa su traktoriaus vieta ({trakt_vieta})."
                    )
                    return render(request, "iranga_komplektavimas.html", ctx)

                # ar jau komplekte?
                cursor.execute("""
                    SELECT 
                        (SELECT COUNT(*) FROM irangos_komplektas WHERE fk_Iranga_id_iranga=%s)
                      + (SELECT COUNT(*) FROM irangos_komplekto_detale WHERE fk_iranga=%s)
                """, [ag_id, ag_id])
                if cursor.fetchone()[0] > 0:
                    ctx = _komplektavimo_kontekstas(
                        "Vienas ar daugiau agregatų jau priklauso kitam komplektui."
                    )
                    return render(request, "iranga_komplektavimas.html", ctx)

            # įterpiam naują komplektą (su traktoriu)
            today = date.today()
            cursor.execute("""
                INSERT INTO irangos_komplektas
                (Pavadinimas, Aprasymas, Sudarymo_data, Paskirtis, fk_Naudotojas_id_Naudotojas, fk_Iranga_id_iranga)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [pavadinimas, aprasymas, today, paskirtis, darbuotojas_id, traktorius_id])
            komplektas_id = cursor.lastrowid

            # pridedam agregatus į naują lentelę
            for ag_id in agregatai_ids:
                cursor.execute("""
                    INSERT INTO irangos_komplekto_detale (fk_komplektas, fk_iranga)
                    VALUES (%s, %s)
                """, [komplektas_id, ag_id])

        return redirect("/iranga/komplektavimas/")

    # GET
    ctx = _komplektavimo_kontekstas()
    return render(request, "iranga_komplektavimas.html", ctx)


def iranga_iskomplektuoti(request, id):
    """Iškomplektuojam – šalinam detales ir patį komplektą."""
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM irangos_komplekto_detale WHERE fk_komplektas=%s", [id])
        cursor.execute("DELETE FROM irangos_komplektas WHERE id_Irangos_komplektas=%s", [id])
    return redirect("/iranga/komplektavimas/")

# HELPERS
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def dictfetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))
