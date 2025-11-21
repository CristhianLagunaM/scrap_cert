import os
from playwright.async_api import async_playwright

async def scrap_indigenas(df_ind, base_output):

    folder = os.path.join(base_output, "INDIGENAS")
    os.makedirs(folder, exist_ok=True)

    grupos = df_ind.groupby("Nro Iden")["Cred"].apply(list).to_dict()
    df_ind["EstadoDescarga"] = "PENDIENTE"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=True)

        for doc, codigos in grupos.items():
            print(f"INDÍGENAS → {doc} → {codigos}")

            page = await context.new_page()

            try:
                await page.goto(
                    "https://datos.mininterior.gov.co/VentanillaUnica/indigenas/censos/Persona",
                    timeout=90000
                )

                tipos = ["TI", "CC"]
                exito = False

                for tipo in tipos:
                    print(f"Intentando INDÍGENAS con {tipo}…")

                    dd = page.locator('button[data-id="IdTipoDocumento"]')
                    await dd.click()
                    await page.locator(".dropdown-menu").get_by_text(tipo, exact=True).click()

                    await page.locator("#NumeroDocumento").fill(str(doc))
                    await page.locator("#btnGenerarCertificado").click()

                    try:
                        await page.wait_for_selector("#MsjNoEncontrado-Label", timeout=3000)
                        print(f"No encontrado INDÍGENAS: {doc} ({tipo})")
                        continue
                    except:
                        pass

                    try:
                        await page.get_by_role("button", name="Aceptar").click()
                    except:
                        continue

                    try:
                        dl = await page.wait_for_event("download", timeout=25000)
                        filename = "-".join(codigos) + ".pdf"
                        await dl.save_as(os.path.join(folder, filename))
                        print(f"✔ PDF descargado: {filename}")
                        exito = True
                        break
                    except:
                        continue

                df_ind.loc[df_ind["Nro Iden"] == doc, "EstadoDescarga"] = (
                    "OK" if exito else "ERROR"
                )

            except Exception as e:
                print(f"ERROR INDÍGENAS {doc}: {e}")
                df_ind.loc[df_ind["Nro Iden"] == doc, "EstadoDescarga"] = "ERROR"

            await page.close()

        await browser.close()

    return df_ind
