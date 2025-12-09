from django.shortcuts import render, redirect
from django.db import connection
from datetime import date

# --- Stripe importai ---
import stripe
from django.conf import settings
from django.urls import reverse

# nustatom secret key iš settings.py
stripe.api_key = settings.STRIPE_SECRET_KEY


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def dictfetchone(cursor):
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None


# ----------------------------------------------------------
# 1. Vartotojo užsakymai
# ----------------------------------------------------------
def uzsakymai_perziura(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/prisijungimas/")

    msg = None
    msg_type = "info"

    # Žinutės iš kitų veiksmų (apmokėjimas, redagavimas ir pan.)
    if request.GET.get("no_unpaid") == "1":
        msg = "Šiuo metu neturite užsakymų, laukiančių apmokėjimo."
    elif request.GET.get("payment_error") == "1":
        msg = "Mokėjimas buvo atšauktas arba nepavyko."
        msg_type = "error"
    elif request.GET.get("payment_ok") == "1":
        msg = "Mokėjimas sėkmingas."
        msg_type = "success"
    elif request.GET.get("cant_edit") == "1":
        msg = "Užsakymo redaguoti nebegalima, nes jis nebelaukia apmokėjimo."
        msg_type = "error"
    elif request.GET.get("cant_cancel") == "1":
        msg = "Užsakymo atšaukti nebegalima, nes jis nebelaukia apmokėjimo."
        msg_type = "error"

    # Pasiimam visus vartotojo užsakymus
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.id_Uzsakymas,
                   u.Busena,
                   u.Kaina,
                   u.Data,
                   COUNT(up.id_Uzsakymo_preke) AS prekiu_kiekis
            FROM uzsakymas u
            LEFT JOIN uzsakymo_preke up
                ON up.fk_Uzsakymas_id_Uzsakymas = u.id_Uzsakymas
            WHERE u.fk_Naudotojas_id_Naudotojas = %s
            GROUP BY u.id_Uzsakymas, u.Busena, u.Kaina, u.Data
            ORDER BY u.id_Uzsakymas DESC
        """, [user_id])
        uzsakymai = dictfetchall(cursor)

    # JEI ŠIAM VARTOTOJUI NĖRA NĖ VIENO UŽSAKYMO → rodome „nėra užsakymų“,
    # bet tik tada, kai dar nėra kitų žinučių (pvz. payment_ok ir pan.)
    if len(uzsakymai) == 0 and msg is None:
        msg = "Šiuo metu neturite jokių užsakymų."
        msg_type = "info"

    has_unpaid = any(u["Busena"] == 1 for u in uzsakymai)

    return render(request, "uzsakymai.html", {
        "uzsakymai": uzsakymai,
        "has_unpaid": has_unpaid,
        "msg": msg,
        "msg_type": msg_type,
    })



# ----------------------------------------------------------
# 2. Naujas užsakymas
# ----------------------------------------------------------
def uzsakymas_naujas(request):

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM preke")
        prekes = dictfetchall(cursor)

    if request.method == "POST":

        naudotojas_id = request.session.get("user_id")

        if not naudotojas_id:
            return redirect("/prisijungimas/")

        prekes_ids = request.POST.getlist("preke")
        kiekiai = request.POST.getlist("kiekis")

        # ---- Skaičiuojame bendrą sumą ----
        bendra_suma = 0
        with connection.cursor() as cursor:
            for pid, kiek in zip(prekes_ids, kiekiai):
                cursor.execute("SELECT Kaina FROM preke WHERE id_Preke = %s", [pid])
                price = cursor.fetchone()[0]
                bendra_suma += float(price) * int(kiek)

        # ---- Užsakymo duomenys ----
        busena = 1  # laukia apmokėjimo
        data = date.today()

        # ---- Įrašome užsakymą ----
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO uzsakymas (Busena, Kaina, Data, fk_Naudotojas_id_Naudotojas)
                VALUES (%s, %s, %s, %s)
            """, [busena, bendra_suma, data, naudotojas_id])

            uzsakymo_id = cursor.lastrowid

            # ---- Įrašome prekes į uzsakymo_preke ----
            for pid, kiek in zip(prekes_ids, kiekiai):
                cursor.execute("""
                    INSERT INTO uzsakymo_preke (Kiekis, fk_Uzsakymas_id_Uzsakymas, fk_Preke_id_Preke)
                    VALUES (%s, %s, %s)
                """, [kiek, uzsakymo_id, pid])

        return redirect("/uzsakymai/")

    return render(request, "naujas_uzsakymas.html", {"prekes": prekes})


# ----------------------------------------------------------
# 3. Redaguoti užsakymą
# ----------------------------------------------------------
def uzsakymas_redaguoti(request, id):

    # ---- Gauname užsakymą ir jo prekes + visas prekes pasirinkimui ----
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM uzsakymas WHERE id_Uzsakymas = %s", [id])
        uzsakymas = dictfetchone(cursor)

        if not uzsakymas:
            return redirect("/uzsakymai/")

        # --- jei būsena ne „laukia apmokėjimo“, redaguoti negalima ---
        if uzsakymas["Busena"] != 1:
            return redirect("/uzsakymai/?cant_edit=1")

        cursor.execute("""
            SELECT up.id_Uzsakymo_preke,
                   up.Kiekis,
                   p.id_Preke,
                   p.Pavadinimas,
                   p.Kaina
            FROM uzsakymo_preke up
            JOIN preke p ON p.id_Preke = up.fk_Preke_id_Preke
            WHERE up.fk_Uzsakymas_id_Uzsakymas = %s
        """, [id])
        uz_prekes = dictfetchall(cursor)

        cursor.execute("SELECT * FROM preke")
        visos_prekes = dictfetchall(cursor)

    if request.method == "POST":
        # esamos eilutės
        ids = request.POST.getlist("up_id")
        kiekiai = request.POST.getlist("kiekis")
        remove_ids = request.POST.getlist("remove_ids")  # gali būti tuščias

        # naujos eilutės
        new_prekes = request.POST.getlist("new_preke")
        new_kiekiai = request.POST.getlist("new_kiekis")

        bendra_kaina = 0

        with connection.cursor() as cursor:
            # 1) pašalinam pažymėtas prekes
            for rid in remove_ids:
                cursor.execute("""
                    DELETE FROM uzsakymo_preke
                    WHERE id_Uzsakymo_preke = %s
                """, [rid])

            # 2) atnaujinam kiekius likusioms ir skaičiuojam kainą
            for up_id, kiek in zip(ids, kiekiai):
                if up_id in remove_ids:
                    continue  # šita eilutė jau ištrinta

                if not kiek:
                    continue
                kiek_int = int(kiek)
                if kiek_int <= 0:
                    continue

                cursor.execute("""
                    SELECT p.Kaina
                    FROM uzsakymo_preke up
                    JOIN preke p ON p.id_Preke = up.fk_Preke_id_Preke
                    WHERE up.id_Uzsakymo_preke = %s
                """, [up_id])
                row = cursor.fetchone()
                if not row:
                    continue
                price = row[0]

                bendra_kaina += float(price) * kiek_int

                cursor.execute("""
                    UPDATE uzsakymo_preke
                    SET Kiekis = %s
                    WHERE id_Uzsakymo_preke = %s
                """, [kiek_int, up_id])

            # 3) pridedam naujas prekes
            for pid, kiek in zip(new_prekes, new_kiekiai):
                if not pid or not kiek:
                    continue
                kiek_int = int(kiek)
                if kiek_int <= 0:
                    continue

                cursor.execute("SELECT Kaina FROM preke WHERE id_Preke = %s", [pid])
                row = cursor.fetchone()
                if not row:
                    continue
                price = row[0]

                bendra_kaina += float(price) * kiek_int

                cursor.execute("""
                    INSERT INTO uzsakymo_preke (Kiekis, fk_Uzsakymas_id_Uzsakymas, fk_Preke_id_Preke)
                    VALUES (%s, %s, %s)
                """, [kiek_int, id, pid])

            # 4) atnaujinam užsakymo bendrą kainą
            cursor.execute("""
                UPDATE uzsakymas
                SET Kaina = %s
                WHERE id_Uzsakymas = %s
            """, [bendra_kaina, id])

        return redirect("/uzsakymai/")

    return render(request, "redaguoti_uzsakyma.html", {
        "uzsakymas": uzsakymas,
        "uz_prekes": uz_prekes,
        "visos_prekes": visos_prekes,
    })


# ----------------------------------------------------------
# 4. Apmokėti VIENĄ užsakymą (Stripe)
# ----------------------------------------------------------
def uzsakymas_apmoketi(request, id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/prisijungimas/")

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM uzsakymas WHERE id_Uzsakymas = %s", [id])
        uzsakymas = dictfetchone(cursor)

    if not uzsakymas:
        return redirect("/uzsakymai/")

    suma = float(uzsakymas["Kaina"])
    amount_cents = int(round(suma * 100))

    if request.method == "POST":
        # --- formos duomenys ---
        vardas      = request.POST.get("vardas")      or ""
        pavarde     = request.POST.get("pavarde")     or ""
        telefonas   = request.POST.get("telefonas")   or ""
        gyvenviete  = request.POST.get("gyvenviete")  or ""
        adresas     = request.POST.get("adresas")     or ""
        pasto_kodas = request.POST.get("pasto_kodas") or ""
        m_budas     = request.POST.get("mokejimo_budas") or "kortele"

        # --- jei grynais: jokių Stripe, tiesiog fiksuojam mokėjimą ---
        if m_budas == "grynais":
            today = date.today()
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO mokejimas
                    (Suma, Apmokejimo_data,
                     Vardas, Pavarde, Telefonas, Gyvenviete, Adresas, Pasto_kodas, Mokejimo_budas,
                     fk_Uzsakymas_id_Uzsakymas, fk_Naudotojas_id_Naudotojas)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    suma, today,
                    vardas, pavarde, telefonas, gyvenviete, adresas, pasto_kodas, m_budas,
                    id, user_id
                ])

                cursor.execute("""
                    UPDATE uzsakymas
                    SET Busena = 2
                    WHERE id_Uzsakymas = %s
                """, [id])

            return redirect("/uzsakymai/?payment_ok=1")

        # --- kortelė / PayPal → Stripe ---
        success_url = request.build_absolute_uri(
            reverse("stripe_success")
        ) + "?session_id={CHECKOUT_SESSION_ID}"

        cancel_url = request.build_absolute_uri(
            reverse("stripe_cancel")
        )

        checkout_session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": settings.STRIPE_CURRENCY,
                    "product_data": {
                        "name": f"Užsakymas #{id}",
                    },
                    "unit_amount": amount_cents,
                },
                "quantity": 1,
            }],
            metadata={
                "mode": "single",
                "order_id": str(id),
                "user_id": str(user_id),
                "vardas": vardas,
                "pavarde": pavarde,
                "telefonas": telefonas,
                "gyvenviete": gyvenviete,
                "adresas": adresas,
                "pasto_kodas": pasto_kodas,
                "mokejimo_budas": m_budas,
            },
            success_url=success_url,
            cancel_url=cancel_url,
        )

        return redirect(checkout_session.url, code=303)

    return render(request, "apmoketi_uzsakyma.html", {
        "mode": "single",
        "uzsakymas": uzsakymas,
        "suma": suma,
    })

# ----------------------------------------------------------
# 5. Apmokėti VISUS laukiančius (Stripe)
# ----------------------------------------------------------
def apmoketi_visus(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/prisijungimas/")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_Uzsakymas, Kaina
            FROM uzsakymas
            WHERE fk_Naudotojas_id_Naudotojas = %s
              AND Busena = 1
            ORDER BY id_Uzsakymas
        """, [user_id])
        uzsakymai = dictfetchall(cursor)

    if not uzsakymai:
        return redirect("/uzsakymai/?no_unpaid=1")

    total = sum(float(u["Kaina"]) for u in uzsakymai)
    amount_cents = int(round(total * 100))
    order_ids = [str(u["id_Uzsakymas"]) for u in uzsakymai]
    count = len(order_ids)

    if request.method == "POST":
        vardas      = request.POST.get("vardas")      or ""
        pavarde     = request.POST.get("pavarde")     or ""
        telefonas   = request.POST.get("telefonas")   or ""
        gyvenviete  = request.POST.get("gyvenviete")  or ""
        adresas     = request.POST.get("adresas")     or ""
        pasto_kodas = request.POST.get("pasto_kodas") or ""
        m_budas     = request.POST.get("mokejimo_budas") or "kortele"

        # grynais – jokių Stripe
        if m_budas == "grynais":
            today = date.today()
            with connection.cursor() as cursor:
                for oid in order_ids:
                    cursor.execute("""
                        SELECT Kaina FROM uzsakymas
                        WHERE id_Uzsakymas = %s
                    """, [oid])
                    row = cursor.fetchone()
                    if not row:
                        continue
                    suma = float(row[0])

                    cursor.execute("""
                        INSERT INTO mokejimas
                        (Suma, Apmokejimo_data,
                         Vardas, Pavarde, Telefonas, Gyvenviete, Adresas, Pasto_kodas, Mokejimo_budas,
                         fk_Uzsakymas_id_Uzsakymas, fk_Naudotojas_id_Naudotojas)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        suma, today,
                        vardas, pavarde, telefonas, gyvenviete, adresas, pasto_kodas, m_budas,
                        oid, user_id
                    ])

                    cursor.execute("""
                        UPDATE uzsakymas
                        SET Busena = 2
                        WHERE id_Uzsakymas = %s
                    """, [oid])

            return redirect("/uzsakymai/?payment_ok=1")

        # kortelė / PayPal → Stripe
        success_url = request.build_absolute_uri(
            reverse("stripe_success")
        ) + "?session_id={CHECKOUT_SESSION_ID}"

        cancel_url = request.build_absolute_uri(
            reverse("stripe_cancel")
        )

        checkout_session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": settings.STRIPE_CURRENCY,
                    "product_data": {
                        "name": f"Visi neapmokėti užsakymai ({count} vnt.)",
                    },
                    "unit_amount": amount_cents,
                },
                "quantity": 1,
            }],
            metadata={
                "mode": "all",
                "order_ids": ",".join(order_ids),
                "user_id": str(user_id),
                "vardas": vardas,
                "pavarde": pavarde,
                "telefonas": telefonas,
                "gyvenviete": gyvenviete,
                "adresas": adresas,
                "pasto_kodas": pasto_kodas,
                "mokejimo_budas": m_budas,
            },
            success_url=success_url,
            cancel_url=cancel_url,
        )

        return redirect(checkout_session.url, code=303)

    return render(request, "apmoketi_uzsakyma.html", {
        "mode": "all",
        "uzsakymai": uzsakymai,
        "suma": total,
        "uzsakymu_kiekis": count,
    })

# ----------------------------------------------------------
# 6. Stripe success / cancel
# ----------------------------------------------------------
def stripe_success(request):
    session_id = request.GET.get("session_id")
    if not session_id:
        return redirect("/uzsakymai/?payment_error=1")

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        return redirect("/uzsakymai/?payment_error=1")

    if session.payment_status != "paid":
        return redirect("/uzsakymai/?payment_error=1")

    mode = session.metadata.get("mode", "single")
    user_id = session.metadata.get("user_id")
    order_ids = []

    if mode == "single":
        order_ids = [session.metadata.get("order_id")]
    elif mode == "all":
        raw = session.metadata.get("order_ids", "")
        order_ids = [oid for oid in raw.split(",") if oid]

    # kontaktiniai duomenys iš Stripe metadata
    vardas      = session.metadata.get("vardas", "")
    pavarde     = session.metadata.get("pavarde", "")
    telefonas   = session.metadata.get("telefonas", "")
    gyvenviete  = session.metadata.get("gyvenviete", "")
    adresas     = session.metadata.get("adresas", "")
    pasto_kodas = session.metadata.get("pasto_kodas", "")
    m_budas     = session.metadata.get("mokejimo_budas", "kortele")

    today = date.today()

    with connection.cursor() as cursor:
        for oid in order_ids:
            if not oid:
                continue

            cursor.execute(
                "SELECT Kaina FROM uzsakymas WHERE id_Uzsakymas = %s",
                [oid],
            )
            row = cursor.fetchone()
            if not row:
                continue
            suma = float(row[0])

            cursor.execute("""
                INSERT INTO mokejimas
                (Suma, Apmokejimo_data,
                 Vardas, Pavarde, Telefonas, Gyvenviete, Adresas, Pasto_kodas, Mokejimo_budas,
                 fk_Uzsakymas_id_Uzsakymas, fk_Naudotojas_id_Naudotojas)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                suma, today,
                vardas, pavarde, telefonas, gyvenviete, adresas, pasto_kodas, m_budas,
                oid, user_id
            ])

            cursor.execute("""
                UPDATE uzsakymas
                SET Busena = 2
                WHERE id_Uzsakymas = %s
            """, [oid])

    return redirect("/uzsakymai/?payment_ok=1")


def stripe_cancel(request):
    return redirect("/uzsakymai/?payment_error=1")


# ----------------------------------------------------------
# 7. Atšaukti užsakymą
# ----------------------------------------------------------
def uzsakymas_atsaukti(request, id):

    if request.method == "POST":

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT Busena FROM uzsakymas
                WHERE id_Uzsakymas = %s
            """, [id])
            row = cursor.fetchone()

        if not row:
            return redirect("/uzsakymai/")

        busena = row[0]

        # Jei nebelaukia apmokėjimo – negalima atšaukti
        if busena != 1:
            return redirect("/uzsakymai/?cant_cancel=1")

        with connection.cursor() as cursor:

            # 1. Ištrinti prekes
            cursor.execute("""
                DELETE FROM uzsakymo_preke
                WHERE fk_Uzsakymas_id_Uzsakymas = %s
            """, [id])

            # 2. Ištrinti patį užsakymą
            cursor.execute("""
                DELETE FROM uzsakymas
                WHERE id_Uzsakymas = %s
            """, [id])

        return redirect("/uzsakymai/")

    return redirect("/uzsakymai/")
