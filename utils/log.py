import json

LOG_GLOBAL = []

def add_log(msg=None, tipo="texto", **data):
    if tipo == "texto":
        LOG_GLOBAL.append(msg)
    elif tipo == "resultado":
        LOG_GLOBAL.append(json.dumps({
            "tipo": "resultado",
            **data
        }))
