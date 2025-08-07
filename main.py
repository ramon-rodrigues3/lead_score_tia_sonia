from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
import requests, bitrix
from datetime import datetime, date
from collections import Counter
app = FastAPI()

@app.post('/lead-score/{id}')
async def gerar_lead_score(id: str):
    try:
        card = bitrix.deal_get(id)
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=500, detail=f"Erro HTTP ao conectar com Bitrix24: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Erro de conexão ao Bitrix24: {err}")
        raise HTTPException(status_code=500, detail=f"Erro de conexão ao Bitrix24: {err}")

    pontuacao = 0

    inicial = card.get('UF_CRM_1753909129252')

    if not inicial:
        return JSONResponse(
            {
                "error": {
                    "code": "MISSING_REQUIRED_FIELD",
                    "message": "O campo (UF_CRM_1716208405435) é um campo obrigatório e não foi encontrado ou está vazio para o negócio fornecido.",
                }
            }, 
            status_code=400
        )
    
    elif inicial == "91":

        resposta1 = card.get('UF_CRM_1753909243')
        match resposta1:
            case "95":
                pass
            case "97":
                pontuacao += 1
            case "99":
                pass

        resposta2 = card.get('UF_CRM_1753909299')
        match resposta2:
            case "101":
                pass
            case "103":
                pontuacao += 1
            case "105":
                pontuacao += 2

        resposta3 = card.get('UF_CRM_1753909359')
        match resposta3:
            case "107":
                pass
            case "109":
                pontuacao += 2
            case "111":
                pontuacao += 3
        
        resposta4 = card.get('UF_CRM_1753909419')
        match resposta4:
            case "113":
                pass
            case "115":
                pontuacao += 2
            case "117":
                pontuacao += 1

        resposta5 = card.get('UF_CRM_1753909481')
        match resposta5:
            case "119":
                pass
            case "121":
                pontuacao += 1
            case "123":
                pontuacao += 2
        
        resposta6 = card.get('UF_CRM_1753909529')
        match resposta6:
            case "125":
                pass
            case "127":
                pontuacao += 1
            case "129":
                pontuacao += 2
        
        resposta7 = card.get('UF_CRM_1753909563')
        match resposta7:
            case "131":
                pass
            case "133":
                pontuacao += 1
            case "135":
                pontuacao += 2

        resposta8 = card.get('UF_CRM_1753909657')
        match resposta8:
            case "137":
                pontuacao += 3
            case "139":
                pontuacao += 1
            case "141":
                pass
        
        resposta9 = card.get('UF_CRM_1753909862')
        match resposta9:
            case "143":
                pontuacao += 3
            case "145":
                pontuacao += 1
            case "147":
                pass

    elif inicial == "93":
        resposta1 = card.get('UF_CRM_1754056899')
        match resposta6:
            case "155":
                pontuacao += 3
            case "157":
                pontuacao += 2
            case "159":
                pass
        
        resposta2 = card.get('UF_CRM_1754056950')
        match resposta2:
            case "161":
                pontuacao += 3
            case "163":
                pontuacao += 1
            case "165":
                pass
        
        resposta3 = card.get('UF_CRM_1754056998')
        match resposta3:
            case "167":
                pontuacao += 3
            case "169":
                pontuacao += 2
            case "171":
                pass
        
        resposta4 = card.get('UF_CRM_1754057056')
        match resposta4:
            case "173":
                pontuacao += 2
            case "175":
                pass
            case "177":
                pontuacao += 1
            case "179":
                pontuacao += 1
        
        resposta5 = card.get('UF_CRM_1754057093')
        match resposta6:
            case "181":
                pontuacao += 3
            case "183":
                pontuacao += 1
            case "185":
                pass
        
        resposta6 = card.get('UF_CRM_1754057136')
        match resposta6:
            case "187":
                pontuacao += 3
            case "189":
                pontuacao += 2
            case "191":
                pass

        resposta7 = card.get('UF_CRM_1753909862')
        match resposta7:
            case "143":
                pontuacao += 3
            case "145":
                pontuacao += 1
            case "147":
                pass
            
    # Perfil DISC

    respostas = []

    disc1 = card.get('UF_CRM_1754337993')
    match disc1:
        case "251":
            respostas.append("a")
        case "253":
            respostas.append("b")
        case "255":
            respostas.append("c")
        case "257":
            respostas.append("d")

    disc2 = card.get('UF_CRM_1754338049')
    match disc2:
        case "259":
            respostas.append("a")
        case "261":
            respostas.append("b")
        case "263":
            respostas.append("c")
        case "265":
            respostas.append("d")
    
    disc3 = card.get('UF_CRM_1754338108')
    match disc3:
        case "267":
            respostas.append("a")
        case "269":
            respostas.append("b")
        case "271":
            respostas.append("c")
        case "273":
            respostas.append("d")

    cod_categoria = {
        "a": "275",
        "b": "277",
        "c": "279",
        "d": "281"
    }

    nome_categoria = {
        "a": "Conforme",
        "b": "Dominante",
        "c": "Estável",
        "d": "Influente"
    }

    contagem = Counter(respostas)
    lista_completa = contagem.most_common()
    mais_comum_contagem = lista_completa[0][1]

    alternativas_mais_comuns = [i[0] for i in lista_completa if i[1] == mais_comum_contagem]
    outras_alternativas = [i[0] for i in lista_completa if i[1] > 0]

    if len(alternativas_mais_comuns) > 1:
        categoria = "301"
        texto = (
            f"Cliente com perfil equlibrado entre os traços"
            ', '.join([nome_categoria.get(categoria) for categoria in alternativas_mais_comuns])
        )
    
    elif len(outras_alternativas) > 0:
        perfil = alternativas_mais_comuns[0]
        traco = outras_alternativas[0]

        categoria = cod_categoria.get(perfil)
        texto = f"Cliente com perfil {nome_categoria.get(perfil)} com traço secundário {nome_categoria.get(traco)}"
    else:
        perfil = alternativas_mais_comuns[0]

        categoria = cod_categoria.get(perfil)
        texto = f"Cliente com perfil predominante {nome_categoria.get(perfil)}"
    
    
    bitrix.deal_update(id, 
        {
            "UF_CRM_1753910152": pontuacao,
            "UF_CRM_1754056679256": "149" if pontuacao > 9 else "151" if pontuacao > 4 else "153",
            "UF_CRM_1754339770821": categoria,
            "UF_CRM_1754339821860": texto
        }
    )
    return JSONResponse(
        {
            "status": "success",
            "message": "Lead Score feito com sucesso.",
        },
        status_code=200
    )
