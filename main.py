from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
import requests, bitrix
from datetime import datetime, date
from collections import Counter
app = FastAPI()

@app.post('/lead-score/')
async def gerar_lead_score(id: str):
    try:
        card = bitrix.deal_get(id)
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=500, detail=f"Erro HTTP ao conectar com Bitrix24: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Erro de conexão ao Bitrix24: {err}")
        raise HTTPException(status_code=500, detail=f"Erro de conexão ao Bitrix24: {err}")
    
    qualificacoes_realizadas = int(card.get('UF_CRM_1757601326310')) if card.get('UF_CRM_1757601326310') else 0

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
                pontuacao += 2
            case "99":
                pontuacao += 1

        resposta2 = card.get('UF_CRM_1753909299')
        match resposta2:
            case "101":
                pass
            case "103":
                pontuacao += 1
            case "105":
                pontuacao += 2
        
        resposta3 = card.get('UF_CRM_1753909862')
        match resposta3:
            case "143":
                pontuacao += 2
            case "145":
                pontuacao += 1
            case "147":
                pass

    elif inicial == "93":
        resposta1 = card.get('UF_CRM_1754056899')
        match resposta1:
            case "155":
                pontuacao += 2
            case "157":
                pontuacao += 1
            case "159":
                pass
        
        resposta2 = card.get('UF_CRM_1754057056')
        match resposta2:
            case "173":
                pontuacao += 2
            case "175":
                pass
            case "177":
                pontuacao += 1
            case "179":
                pontuacao += 1

        resposta3 = card.get('UF_CRM_1757618101')
        match resposta3:
            case "811":
                pontuacao += 2
            case "813":
                pontuacao += 1
            case "815":
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

    categoria = None

    if respostas:
        contagem = Counter(respostas)
        lista_completa = contagem.most_common()
        mais_comum_contagem = lista_completa[0][1]

        alternativas_mais_comuns = [i[0] for i in lista_completa if i[1] == mais_comum_contagem]
        outras_alternativas = [i[0] for i in lista_completa if i[1] > 0 and i[1] < mais_comum_contagem]

        if len(alternativas_mais_comuns) > 1:
            categoria = "301"
            texto = "Cliente com perfil equlibrado entre os traços " + ', '.join([nome_categoria.get(categoria) for categoria in alternativas_mais_comuns])
        
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
            "UF_CRM_1754056679256": "149" if pontuacao > 4 else "151" if pontuacao > 2 else "153",
            "UF_CRM_1754339770821": categoria,
            "UF_CRM_1754339821860": texto
        }
    )
    

    if qualificacoes_realizadas < 1:
        del card['ID']
        card['STAGE_ID'] = "C5:NEW"
        card['CATEGORY_ID'] = "5"
        card["UF_CRM_1753910152"] = pontuacao,
        card["UF_CRM_1754056679256"] = "149" if pontuacao > 4 else "151" if pontuacao > 2 else "153",
        card['UF_CRM_1754339770821'] = categoria
        card['UF_CRM_1754339821860'] = texto
        bitrix.deal_add(card)

    return JSONResponse(
        {
            "status": "success",
            "message": "Lead Score feito com sucesso.",
        },
        status_code=200
    )

@app.post('/resolver-sac')
async def resolver_sac(id: str):
    try:
        card = bitrix.deal_get(id)
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=500, detail=f"Erro HTTP ao conectar com Bitrix24: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Erro de conexão ao Bitrix24: {err}")
        raise HTTPException(status_code=500, detail=f"Erro de conexão ao Bitrix24: {err}")
    
    codigo_cliente = card.get('UF_CRM_1754329595153')
    etapa = card.get('STAGE_ID')

    if etapa != 'C7:LOSE' and etapa != 'C7:WON':
        return JSONResponse(
            {
                "error": {
                    "code": "UNEXPECTED_COLUMN",
                    "message": "O negócio não está na coluna esperada.",
                }
            }, 
            status_code=400
        )
    
    if not codigo_cliente:
        return JSONResponse(
            {
                "error": {
                    "code": "MISSING_REQUIRED_FIELD",
                    "message": "O campo (UF_CRM_1754329595153) é um campo obrigatório e não foi encontrado ou está vazio para o negócio fornecido.",
                }
            }, 
            status_code=400
        )
    
    equivalentes = bitrix.deal_list({"=UF_CRM_1754329595153": codigo_cliente, "STAGE_ID": "C5:UC_PT3G7E"}, 
        ["UF_CRM_1756322314808", "UF_CRM_1756322358546", "UF_CRM_1756326992416", "UF_CRM_1756408133187"])

    if not equivalentes:
        return JSONResponse(
            {
                "error": {
                    "code": "PARTIAL_SUCESS",
                    "message": "O negócio foi processado, mas não foi encontrado equivalente no funil '5'.",
                }
            }, 
            status_code=200
        )

    for equivalente in equivalentes:
        equivalente_id = equivalente.get('ID')

        bitrix.deal_update(equivalente_id, {
            "STAGE_ID": 'C5:UC_5PKU1M',
            "UF_CRM_1756322314808": equivalente.get("UF_CRM_1756322314808"),
            "UF_CRM_1756322358546": equivalente.get("UF_CRM_1756322358546"),
            "UF_CRM_1756326992416": equivalente.get("UF_CRM_1756326992416"),
            "UF_CRM_1756408133187": equivalente.get("UF_CRM_1756408133187")
        })
    

    return JSONResponse(
        {
            "error": {
                "code": "SUCESS",
                "message": "O negócio foi processado e todos os negócios equivalentes foram atualizados no funil '5'.",
            }
        }, 
        status_code=200
    )
    # Solução encontrada = UF_CRM_1756322314808
    # Como foi a solução = UF_CRM_1756322358546
    # Motivo para não resolução = UF_CRM_1756326992416
    # Resultado do SAC = UF_CRM_1756408133187

    # Código do Cliente - UF_CRM_1754329595153

@app.post("/validacao-cadastro")
async def validacao_cadastro(id: str):
    try:
        card = bitrix.deal_get(id)
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=500, detail=f"Erro HTTP ao conectar com Bitrix24: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Erro de conexão ao Bitrix24: {err}")
        raise HTTPException(status_code=500, detail=f"Erro de conexão ao Bitrix24: {err}")
    
    etapa = card.get('STAGE_ID')
    id_contato = card.get('CONTACT_ID')

    # Cadastro Não Validado 
    if etapa == "C3:PREPAYMENT_INVOICE":
        equivalentes = bitrix.deal_list({"CATEGORY_ID": "", "=CONTACT_ID": id_contato, "STAGE_ID": "8"}, [])

        if not equivalentes:
            return JSONResponse(
                {
                    "error": {
                        "code": "PARTIAL_SUCESS",
                        "message": "O negócio foi processado, mas não foi encontrado um equivalente",
                    }
                }, 
                status_code=200
            )
        
        equivalente = equivalentes[0]
        equivalente_id = equivalente.get('ID')

        bitrix.deal_update(equivalente_id, 
            {
                "UF_CRM_1754332136594": card.get('UF_CRM_1754332136594'), # Motivo da não validação de cadastro
                "UF_CRM_1757599499747": card.get('UF_CRM_1757599499747'), # Detalhes da não validação de cadastro
                "STAGE_ID": "9"
            }
        )

        return JSONResponse(
            {
                "status": "success",
                "message": "O negócio equivalente foi atualizado com sucesso.",
            },
            status_code=200
        )

    # Cadastro Validado
    elif etapa == "C3:PREPARATION":
        equivalentes = bitrix.deal_list({"CATEGORY_ID": "", "=CONTACT_ID": id_contato, "STAGE_ID": "8"}, [])

        if not equivalentes:
            return JSONResponse(
                {
                    "error": {
                        "code": "PARTIAL_SUCESS",
                        "message": "O negócio foi processado, mas não foi encontrado um equivalente",
                    }
                }, 
                status_code=200
            )
        
        equivalente = equivalentes[0]
        equivalente_id = equivalente.get('ID')

        bitrix.deal_update(equivalente_id, 
            {
                "UF_CRM_1754330259328": card.get("UF_CRM_1754330259328"), # Limite de Crédito
                "UF_CRM_1754329595153": card.get("UF_CRM_1754329595153"), # Código do Cliente
                "STAGE_ID": "WON"
            }
        )

        return JSONResponse(
            {
                "status": "success",
                "message": "O negócio equivalente foi atualizado com sucesso.",
            },
            status_code=200
        )

    else:
        return JSONResponse(
            {
                "error": {
                    "code": "UNEXPECTED_COLUMN",
                    "message": "O negócio não está na coluna esperada.",
                }
            }, 
            status_code=400
        )
    
@app.post("/validacao-cadastro-recuperacao")
async def validacao_cadastro_recuperacao(id: str):
    try:
        card = bitrix.deal_get(id)
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=500, detail=f"Erro HTTP ao conectar com Bitrix24: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Erro de conexão ao Bitrix24: {err}")
        raise HTTPException(status_code=500, detail=f"Erro de conexão ao Bitrix24: {err}")
    
    etapa = card.get('STAGE_ID')
    id_contato = card.get('CONTACT_ID')

    # Cadastro Não Aprovado 
    if etapa == "C3:PREPAYMENT_INVOICE":
        equivalentes = bitrix.deal_list({"CATEGORY_ID": "17", "=CONTACT_ID": id_contato, "STAGE_ID": "C17:UC_5PGFYS"}, [])

        if not equivalentes:
            return JSONResponse(
                {
                    "error": {
                        "code": "PARTIAL_SUCESS",
                        "message": "O negócio foi processado, mas não foi encontrado um equivalente",
                    }
                }, 
                status_code=200
            )
        
        equivalente = equivalentes[0]
        equivalente_id = equivalente.get('ID')

        bitrix.deal_update(equivalente_id, 
            {
                "UF_CRM_1754332136594": card.get('UF_CRM_1754332136594'), # Motivo da não validação de cadastro
                "UF_CRM_1757599499747": card.get('UF_CRM_1757599499747'), # Detalhes da não validação de cadastro
                "STAGE_ID": "C17:UC_6IM0A1"
            }
        )

        return JSONResponse(
            {
                "status": "success",
                "message": "O negócio equivalente foi atualizado com sucesso.",
            },
            status_code=200
        )

    # Cadastro Aprovado
    elif etapa == "C3:PREPARATION":
        equivalentes = bitrix.deal_list({"CATEGORY_ID": "17", "=CONTACT_ID": id_contato, "STAGE_ID": "C17:UC_5PGFYS"}, [])

        if not equivalentes:
            return JSONResponse(
                {
                    "error": {
                        "code": "PARTIAL_SUCESS",
                        "message": "O negócio foi processado, mas não foi encontrado um equivalente",
                    }
                }, 
                status_code=200
            )
        
        equivalente = equivalentes[0]
        equivalente_id = equivalente.get('ID')

        bitrix.deal_update(equivalente_id, 
            {
                "UF_CRM_1754330259328": card.get("UF_CRM_1754330259328"), # Limite de Crédito
                "UF_CRM_1754329595153": card.get("UF_CRM_1754329595153"), # Código do Cliente
                "STAGE_ID": "C17:WON"
            }
        )

        return JSONResponse(
            {
                "status": "success",
                "message": "O negócio equivalente foi atualizado com sucesso.",
            },
            status_code=200
        )

    else:
        return JSONResponse(
            {
                "error": {
                    "code": "UNEXPECTED_COLUMN",
                    "message": "O negócio não está na coluna esperada.",
                }
            }, 
            status_code=400
        )

@app.post("/aprovacao-credito")
async def aprovacao_credito(id: str):
    try:
        card = bitrix.deal_get(id)
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=500, detail=f"Erro HTTP ao conectar com Bitrix24: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Erro de conexão ao Bitrix24: {err}")
        raise HTTPException(status_code=500, detail=f"Erro de conexão ao Bitrix24: {err}")
    
    codigo_cliente = card.get('UF_CRM_1754329595153')
    etapa = card.get('STAGE_ID')

    # Crédito Reprovado
    if etapa == "C3:4":
        equivalentes = bitrix.deal_list(
            {"CATEGORY_ID": "5", "STAGE_ID": "C5:17" , "=UF_CRM_1754329595153": codigo_cliente}, [])

        if not equivalentes: 
            return JSONResponse(
                {
                    "error": {
                        "code": "PARTIAL_SUCESS",
                        "message": "O negócio foi processado, mas não foi encontrado um equivalente",
                    }
                }, 
                status_code=200
            )

        equivalente = equivalentes[0]
        equivalente_id = equivalente.get("ID")

        bitrix.deal_update(equivalente_id, 
            {
                "UF_CRM_1757621126849": card.get("UF_CRM_1757621126849"), # Motivo para reprovação do crédito
                "UF_CRM_1754335532954": card.get("UF_CRM_1754335532954"), # O cliente pode comprar à vista?
                "STAGE_ID": "C5:19"
            }
        )

        return JSONResponse(
            {
                "status": "success",
                "message": "O negócio equivalente foi atualizado com sucesso.",
            },
            status_code=200
        )

    # Crédito Aprovado
    elif etapa == "C3:5":
        equivalentes = bitrix.deal_list(
            {"CATEGORY_ID": "5", "STAGE_ID": "C5:17" , "=UF_CRM_1754329595153": codigo_cliente}, [])

        if not equivalentes: 
            return JSONResponse(
                {
                    "error": {
                        "code": "PARTIAL_SUCESS",
                        "message": "O negócio foi processado, mas não foi encontrado um equivalente",
                    }
                }, 
                status_code=200
            )

        equivalente = equivalentes[0]
        equivalente_id = equivalente.get("ID")

        bitrix.deal_update(equivalente_id, {"STAGE_ID": "C5:18"})
        return JSONResponse(
            {
                "status": "success",
                "message": "O negócio equivalente foi atualizado com sucesso.",
            },
            status_code=200
        )

    else:
        return JSONResponse(
            {
                "error": {
                    "code": "UNEXPECTED_COLUMN",
                    "message": "O negócio não está na coluna esperada.",
                }
            }, 
            status_code=400
        )

@app.post("/verificacao-pedido")
async def verificacao_pedido(id: str):
    try:
        card = bitrix.deal_get(id)
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=500, detail=f"Erro HTTP ao conectar com Bitrix24: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Erro de conexão ao Bitrix24: {err}")
        raise HTTPException(status_code=500, detail=f"Erro de conexão ao Bitrix24: {err}")
    
    codigo_pedido = card.get('UF_CRM_1757624409905')
    etapa = card.get('STAGE_ID')

    if etapa == "C3:UC_XCFLIY":
        equivalentes = bitrix.deal_list(
            {"CATEGORY_ID": "9", "STAGE_ID": "C9:PREPARATION", "=UF_CRM_1757624409905": codigo_pedido}, [])

        if not equivalentes: 
            return JSONResponse(
                {
                    "error": {
                        "code": "PARTIAL_SUCESS",
                        "message": "O negócio foi processado, mas não foi encontrado um equivalente",
                    }
                }, 
                status_code=200
            )

        equivalente = equivalentes[0]
        equivalente_id = equivalente.get("ID")

        bitrix.deal_update(equivalente_id, 
            {
                "UF_CRM_1757625375106": card.get("UF_CRM_1757625375106"), # Observações do financeiro sobre o pedido
                "STAGE_ID": "C9:UC_KK4CXQ" 
            }
        )
    else:
        return JSONResponse(
            {
                "error": {
                    "code": "UNEXPECTED_COLUMN",
                    "message": "O negócio não está na coluna esperada.",
                }
            }, 
            status_code=400
        )

@app.post("/atualizacao-pedido")
async def atualizacao_pedido(id: str):
    try:
        card = bitrix.deal_get(id)
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=500, detail=f"Erro HTTP ao conectar com Bitrix24: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Erro de conexão ao Bitrix24: {err}")
        raise HTTPException(status_code=500, detail=f"Erro de conexão ao Bitrix24: {err}")
    
    codigo_pedido = card.get('UF_CRM_1757624409905')
    etapa = card.get('STAGE_ID')

    if etapa == "C11:WON" or etapa == "C11:LOSE":
        equivalentes = bitrix.deal_list(
            {"CATEGORY_ID": "9", "=UF_CRM_1757624409905": codigo_pedido}, [])

        if not equivalentes: 
            return JSONResponse(
                {
                    "error": {
                        "code": "PARTIAL_SUCESS",
                        "message": "O negócio foi processado, mas não foi encontrado um equivalente",
                    }
                }, 
                status_code=200
            )

        equivalente = equivalentes[0]
        equivalente_id = equivalente.get("ID")

        bitrix.deal_update(equivalente_id, 
            {
                "UF_CRM_1757626001233": card.get("UF_CRM_1757626001233"), # Observações da logística sobre o pedido
                "STAGE_ID": "C9:UC_KK4CXQ"
            }
        )

        return JSONResponse(
            {
                "status": "success",
                "message": "O negócio equivalente foi atualizado com sucesso.",
            },
            status_code=200
        )

    else:
        return JSONResponse(
            {
                "error": {
                    "code": "UNEXPECTED_COLUMN",
                    "message": "O negócio não está na coluna esperada.",
                }
            }, 
            status_code=400
        )
