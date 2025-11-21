import os
from playwright.async_api import async_playwright

# Flags necesarios para correr Chromium en Railway (Linux sin sandbox)
CHROMIUM_ARGS = [
    "--disable-dev-shm-usage",
    "--disable-setuid-sandbox",
    "--no-sandbox",
    "--no-zygote",
    "--single-process",
]

async def scrap_indigenas(df_ind, base_output):

    folder = os.path.join(base_output, "INDIGENAS")
    os.makedirs(folder, exist_ok=True)

    grupos = df_ind.groupby("Nro Iden")["Cred"].apply(list).to_dict()
    df_ind["EstadoDescarga"] = "PENDIENTE"

    async with async_playwright() as p:

        # Chromium compatible con Railway
        browser = await p.chromium.launch(
            headless=True,
            args=CHROMIUM_ARGS
        )
        context = await browser.new_context(accept_downloads=True)

        for doc, codigos in grupos.items():
            print(f"[INDIGENAS] Procesando {doc} → {codigos}")

            page = await context.new_page()

            try:
                await page.goto(
                    "https://datos.mininterior.gov.co/VentanillaUnica/indigenas/censos/Persona",
                    timeout=120000
                )

                tipos = ["TI", "CC"]
                exito = False

                for tipo in tipos:
                    print(f"[INDIGENAS] Intentando con tipo {tipo}")

                    dd = page.locator('button[data-id="IdTipoDocumento"]')
                    await dd.click()
                    await page.locator(".dropdown-menu").get_by_text(
                        tipo, exact=True
                    ).click()

                    await page.locator("#NumeroDocumento").fill(str(doc))
                    await page.locator("#btnGenerarCertificado").click()

                    # Detectar "no encontrado"
                    try:
                        await page.wait_for_selector("#MsjNoEncontrado-Label", timeout=3000)
                        print(f"[INDIGENAS] ❌ No encontrado {doc} ({tipo})")
                        continue
                    except:
                        pass

                    # Modal "Aceptar"
                    try:
                        await page.get_by_role("button", name="Aceptar").click()
                    except:
                        pass

                    # Intento de descarga
                    try:
                        dl = await page.wait_for_event("download", timeout=30000)
                        filename = "-".join(codigos) + ".pdf"
                        save_path = os.path.join(folder, filename)
                        await dl.save_as(save_path)

                        print(f"[INDIGENAS] ✔ Descargado: {filename}")
                        exito = True
                        break

                    except Exception as e:
                        print(f"[INDIGENAS] Error descargando: {e}")
                        continue

                df_ind.loc[df_ind["Nro Iden"] == doc, "EstadoDescarga"] = (
                    "OK" if exito else "ERROR"
                )

            except Exception as e:
                print(f"[INDIGENAS] ❌ Error general con {doc}: {e}")
                df_ind.loc[df_ind["Nro Iden"] == doc, "EstadoDescarga"] = "ERROR"

            await page.close()

        await browser.close()

    return df_ind
