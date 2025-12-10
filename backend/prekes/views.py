from django.shortcuts import render, redirect
from django.db import connection

# helperiai tokie pat, kaip uzsakymai/iranga
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def dictfetchone(cursor):
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None


# ----------------------------------------------------------
# 1. Prekių katalogas
# ----------------------------------------------------------
def prekiu_sarasas(request):
    msg = None
    msg_success = None

    if request.GET.get("preke_nera") == "1":
        msg = "Tokios prekės sandėlyje nerasta."

    if request.GET.get("added") == "1":
        msg_success = "Prekė sėkmingai pridėta."

    if request.GET.get("deleted") == "1":
        msg_success = "Prekė sėkmingai panaikinta."

    if request.GET.get("cannot_delete") == "1":
        msg = "Prekės panaikinti negalima, nes ji naudojama užsakymuose."

    filter_kat = (request.GET.get("kategorija") or "").strip()
    filter_q   = (request.GET.get("q") or "").strip()
    filter_min = (request.GET.get("kaina_nuo") or "").strip()
    filter_max = (request.GET.get("kaina_iki") or "").strip()

    where_parts = []
    params = []

    if filter_kat:
        where_parts.append("p.Kategorija = %s")
        params.append(filter_kat)

    if filter_q:
        where_parts.append("(p.Pavadinimas LIKE %s OR p.Aprasymas LIKE %s)")
        like_val = f"%{filter_q}%"
        params.extend([like_val, like_val])

    if filter_min:
        try:
            float(filter_min.replace(",", "."))
            where_parts.append("p.Kaina >= %s")
            params.append(filter_min.replace(",", "."))
        except ValueError:
            pass

    if filter_max:
        try:
            float(filter_max.replace(",", "."))
            where_parts.append("p.Kaina <= %s")
            params.append(filter_max.replace(",", "."))
        except ValueError:
            pass

    where_sql = ""
    if where_parts:
        where_sql = "WHERE " + " AND ".join(where_parts)

    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT 
                p.id_Preke,
                p.Pavadinimas,
                p.Kaina,
                p.Kategorija,
                p.Matavimo_vienetas,
                COALESCE(SUM(l.Kiekis), 0) AS Bendras_likutis
            FROM preke p
            LEFT JOIN likutis l
              ON l.fk_Preke_id_Preke = p.id_Preke
            {where_sql}
            GROUP BY 
                p.id_Preke, p.Pavadinimas, p.Kaina,
                p.Kategorija, p.Matavimo_vienetas
            ORDER BY p.Pavadinimas
        """, params)
        prekes = dictfetchall(cursor)

    return render(request, "prekiu_sarasas.html", {
        "prekes": prekes,
        "msg": msg,
        "msg_success": msg_success,
        "filter_kat": filter_kat,
        "filter_q": filter_q,
        "filter_min": filter_min,
        "filter_max": filter_max,
    })


# ----------------------------------------------------------
# 2. Vienos prekės peržiūra
# ----------------------------------------------------------
def preke_perziura(request, id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.*,
                COALESCE(SUM(l.Kiekis), 0) AS Bendras_likutis
            FROM preke p
            LEFT JOIN likutis l
              ON l.fk_Preke_id_Preke = p.id_Preke
            WHERE p.id_Preke = %s
            GROUP BY 
                p.id_Preke, p.Pavadinimas, p.Kaina,
                p.Kategorija, p.Aprasymas, p.Matavimo_vienetas
        """, [id])
        preke = dictfetchone(cursor)

    if not preke:
        return redirect("/prekiu_sarasas/?preke_nera=1")

    return render(request, "preke_perziura.html", {
        "preke": preke,
    })

def preke_nauja(request):
    """
    Prekės pridėjimas:
    - GET: rodo formą
    - POST: tikrina ar prekė nepasikartoja ir, jei ok, įrašo į DB (preke + keli likučiai skirtinguose sandėliuose)
    """
    msg = None
    msg_type = "info"

    # Visada pasiimam sandėlius pasirinkimui
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_Sandelis, Pavadinimas
            FROM sandelis
            ORDER BY Pavadinimas
        """)
        sandeliai = dictfetchall(cursor)

    if request.method == "POST":
        pavadinimas = (request.POST.get("pavadinimas") or "").strip()
        kaina_raw   = (request.POST.get("kaina") or "").strip()
        aprasymas   = (request.POST.get("aprasymas") or "").strip()
        kat_raw     = (request.POST.get("kategorija") or "").strip()
        mat_vnt     = (request.POST.get("matavimo_vienetas") or "").strip()

        # Šitos dvi reikšmės ateina kaip sąrašai, nes eilučių gali būti daugiau nei viena
        sandelis_ids = request.POST.getlist("sandelis_id")
        likuciai_raw = request.POST.getlist("likutis")

        # ---- Bazinė validacija (pavadinimas / kaina / kategorija) ----
        if not pavadinimas or not kaina_raw:
            msg = "Pavadinimas ir kaina yra privalomi."
            msg_type = "error"
        elif not kat_raw:
            msg = "Pasirinkite prekės kategoriją."
            msg_type = "error"
        else:
            # Kaina
            kaina_clean = kaina_raw.replace(",", ".")
            try:
                kaina = float(kaina_clean)
            except ValueError:
                msg = "Neteisingas kainos formatas."
                msg_type = "error"
            else:
                # Kategorija (1–5)
                try:
                    kategorija = int(kat_raw)
                except ValueError:
                    msg = "Neteisinga kategorija."
                    msg_type = "error"
                    kategorija = None
                else:
                    if kategorija not in [1, 2, 3, 4, 5]:
                        msg = "Neteisinga kategorija."
                        msg_type = "error"

        # ---- Apdorojam pradinius likučius (daug eilučių) ----
        initial_stocks = []  # sąrašas (sandelis_id, kiekis)

        if msg is None:
            for sid, lr in zip(sandelis_ids, likuciai_raw):
                sid = (sid or "").strip()
                lr = (lr or "").strip()

                # Tuščia eilutė – praleidžiam
                if not sid and not lr:
                    continue

                # Yra kiekis, bet nėra sandėlio -> klaida
                if lr and not sid:
                    msg = "Jei nurodote likutį, pasirinkite sandėlį."
                    msg_type = "error"
                    break

                # Yra sandėlis ir kažkas parašyta kiekio laukelyje
                if sid and lr:
                    try:
                        qty = int(lr)
                    except ValueError:
                        msg = "Neteisingas likučio formatas."
                        msg_type = "error"
                        break

                    if qty < 0:
                        msg = "Likutis negali būti mažesnis už 0."
                        msg_type = "error"
                        break

                    if qty > 0:
                        initial_stocks.append((int(sid), qty))
                # jei sid yra, bet lr tuščias -> tiesiog ignoruojam (nenurodyta reikšmė)

        # ---- Jei klaidų nėra – rašom į DB ----
        if msg is None:
            with connection.cursor() as cursor:
                # ar tokia prekė jau egzistuoja?
                cursor.execute("""
                    SELECT id_Preke
                    FROM preke
                    WHERE Pavadinimas = %s
                """, [pavadinimas])
                existing = cursor.fetchone()

                if existing:
                    msg = "Prekė su tokiu pavadinimu jau egzistuoja."
                    msg_type = "error"
                else:
                    # 1) Įrašom naują prekę (su kategorija)
                    cursor.execute("""
                        INSERT INTO preke (Pavadinimas, Kaina, Aprasymas, Kategorija, Matavimo_vienetas)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [pavadinimas, kaina, aprasymas, kategorija, mat_vnt])

                    preke_id = cursor.lastrowid

                    # 2) Įrašom visus nurodytus likučius į skirtingus sandėlius
                    for sid, qty in initial_stocks:
                        cursor.execute("""
                            INSERT INTO likutis (Kiekis, fk_Preke_id_Preke, fk_Sandelis_id_Sandelis)
                            VALUES (%s, %s, %s)
                        """, [qty, preke_id, sid])

                    # 3) Sėkmės atvejis – grįžtam į katalogą
                    return redirect("/prekiu_sarasas/?added=1")

    return render(request, "preke_nauja.html", {
        "msg": msg,
        "msg_type": msg_type,
        "sandeliai": sandeliai,
    })

def preke_istrinti(request, id):
    """
    Prekės panaikinimas be archyvavimo.
    Jei prekė jau naudota užsakymuose – trinti neleidžiame.
    """
    if request.method != "POST":
        return redirect("/prekiu_sarasas/")

    with connection.cursor() as cursor:
        # patikrinam, ar prekė naudota užsakymuose
        cursor.execute("""
            SELECT COUNT(*)
            FROM uzsakymo_preke
            WHERE fk_Preke_id_Preke = %s
        """, [id])
        count = cursor.fetchone()[0]

        if count > 0:
            # negalima trinti – yra susijusių užsakymų
            return redirect("/prekiu_sarasas/?cannot_delete=1")

        # 1) panaikinam visus likučius tos prekės
        cursor.execute("""
            DELETE FROM likutis
            WHERE fk_Preke_id_Preke = %s
        """, [id])

        # 2) panaikinam pačią prekę
        cursor.execute("""
            DELETE FROM preke
            WHERE id_Preke = %s
        """, [id])

    return redirect("/prekiu_sarasas/?deleted=1")

def likuciu_zemelapis(request, preke_id):
    # 1. Pasiimam prekę
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT *
            FROM preke
            WHERE id_Preke = %s
        """, [preke_id])
        preke = dictfetchone(cursor)

        if not preke:
            return redirect("/prekiu_sarasas/?preke_nera=1")

        # 2. Sandėliai, kuriuose yra tos prekės likutis
        cursor.execute("""
            SELECT 
                s.id_Sandelis,
                s.Pavadinimas,
                s.Adresas,
                s.Platuma,
                s.Ilguma,
                l.Kiekis
            FROM likutis l
            JOIN sandelis s 
              ON s.id_Sandelis = l.fk_Sandelis_id_Sandelis
            WHERE l.fk_Preke_id_Preke = %s
              AND l.Kiekis > 0
        """, [preke_id])
        sandeliai = dictfetchall(cursor)

    return render(request, "likuciu_zemelapis.html", {
        "preke": preke,
        "sandeliai": sandeliai,
    })
