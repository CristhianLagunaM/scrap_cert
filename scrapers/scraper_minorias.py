import os
from playwright.async_api import async_playwright

async def scrap_minorias(df_minorias, base_output):

    folder = os.path.join(base_output, "MINORIAS")
    os.makedirs(folder, exist_ok=True)

    grupos = df_minorias.groupby("Nro Iden")["Cred"].apply(list).to_dict()
    df_minorias["EstadoDescarga"] = "PENDIENTE"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=True)

        for doc, codigos in grupos.items():
            print(f"MINORIAS → {doc} → {codigos}")

            page = await context.new_page()

            try:
                await page.goto(
                    "https://datos.mininterior.gov.co/VentanillaUnica/Dacnrp/auto-reconocimiento/certificado",
                    timeout=90000
                )

                tipos = ["Tarjeta de identidad", "Cédula de ciudadanía"]
                exito = False

                for tipo in tipos:
                    print(f"Intentando MINORIAS con {tipo}…")

                    dd = page.locator('button[data-id="IdTipoDocumento"]')
                    await dd.click()
                    await page.locator(".dropdown-menu").get_by_text(tipo, exact=True).click()

                    await page.locator("#NumeroIdentificacion").fill(str(doc))

                    await page.locator('button[data-id="IdTipoCertificacion"]').click()
                    await page.locator(".dropdown-menu").get_by_text(
                        "Solicitud de autoreconocimiento", exact=True
                    ).click()

                    await page.locator("#SubmitBtn").click()

                    try:
                        await page.wait_for_selector("#MsjNoEncontrado-Label", timeout=3000)
                        print(f"NO encontrado: {doc} ({tipo})")
                        continue
                    except:
                        pass

                    try:
                        await page.get_by_role("button", name="Aceptar").click()
                    except:
                        continue

                    try:
                        dl = await page.wait_for_event("download", timeout=20000)
                        filename = "-".join(codigos) + ".pdf"
                        await dl.save_as(os.path.join(folder, filename))
                        print(f"✔ PDF descargado: {filename}")
                        exito = True
                        break
                    except:
                        continue

                df_minorias.loc[df_minorias["Nro Iden"] == doc, "EstadoDescarga"] = (
                    "OK" if exito else "ERROR"
                )

            except Exception as e:
                print(f"Error MINORIAS {doc}: {e}")
                df_minorias.loc[df_minorias["Nro Iden"] == doc, "EstadoDescarga"] = "ERROR"

            await page.close()

        await browser.close()

    return df_minorias
