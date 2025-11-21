import os
from playwright.async_api import async_playwright

# Flags necesarios para ejecutar Chromium en Railway (Linux sin sandbox)
CHROMIUM_ARGS = [
    "--disable-dev-shm-usage",
    "--disable-setuid-sandbox",
    "--no-sandbox",
    "--no-zygote",
    "--single-process",
]

async def scrap_minorias(df_minorias, base_output):

    # Asegurar carpeta de salida
    folder = os.path.join(base_output, "MINORIAS")
    os.makedirs(folder, exist_ok=True)

    # Agrupar por documento → creds
    grupos = df_minorias.groupby("Nro Iden")["Cred"].apply(list).to_dict()
    df_minorias["EstadoDescarga"] = "PENDIENTENTE"

    async with async_playwright() as p:

        # Lanzar Chromium compatible con Railway
        browser = await p.chromium.launch(
            headless=True,
            args=CHROMIUM_ARGS
        )

        context = await browser.new_context(accept_downloads=True)

        for doc, codigos in grupos.items():
            print(f"[MINORIAS] Procesando {doc} → {codigos}")

            page = await context.new_page()

            try:
                await page.goto(
                    "https://datos.mininterior.gov.co/VentanillaUnica/Dacnrp/auto-reconocimiento/certificado",
                    timeout=120000
                )

                tipos = ["Tarjeta de identidad", "Cédula de ciudadanía"]
                exito = False

                for tipo in tipos:
                    print(f"[MINORIAS] Intento con tipo {tipo}")

                    # Tipo documento
                    dd = page.locator('button[data-id="IdTipoDocumento"]')
                    await dd.click()
                    await page.locator(".dropdown-menu").get_by_text(
                        tipo, exact=True
                    ).click()

                    # Número
                    await page.locator("#NumeroIdentificacion").fill(str(doc))

                    # Tipo certificación
                    await page.locator('button[data-id="IdTipoCertificacion"]').click()
                    await page.locator(".dropdown-menu").get_by_text(
                        "Solicitud de autoreconocimiento", exact=True
                    ).click()

                    # Buscar
                    await page.locator("#SubmitBtn").click()

                    # No encontrado
                    try:
                        await page.wait_for_selector("#MsjNoEncontrado-Label", timeout=3000)
                        print(f"[MINORIAS] ❌ No encontrado con {tipo}")
                        continue
                    except:
                        pass

                    # Modal
                    try:
                        await page.get_by_role("button", name="Aceptar").click()
                    except:
                        pass

                    # Descargar
                    try:
                        dl = await page.wait_for_event("download", timeout=30000)
                        filename = "-".join(codigos) + ".pdf"
                        save_path = os.path.join(folder, filename)
                        await dl.save_as(save_path)

                        print(f"[MINORIAS] ✔ Descargado: {filename}")
                        exito = True
                        break
                    except Exception as e:
                        print(f"[MINORIAS] Error descargando: {e}")
                        continue

                # Marcar estado
                df_minorias.loc[df_minorias["Nro Iden"] == doc, "EstadoDescarga"] = (
                    "OK" if exito else "ERROR"
                )

            except Exception as e:
                print(f"[MINORIAS] ❌ Error general con {doc}: {e}")
                df_minorias.loc[df_minorias["Nro Iden"] == doc, "EstadoDescarga"] = "ERROR"

            await page.close()

        await browser.close()

    return df_minorias
