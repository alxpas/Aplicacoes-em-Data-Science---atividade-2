from datetime import datetime
from src.id_transacao import gerar_id_transacao

def limpar_formulario():
    """Limpa todos os campos do formulário"""
    novo_id = gerar_id_transacao()
    data_hoje = datetime.now().strftime("%d-%m-%y")

    return (
        novo_id,            # id_transacao
        data_hoje,          # data_venda
        "",                 # produto
        0.0,                # preco_unitario
        0,                  # quantidade
        "",                 # nome_cliente
        "",                 # cidade
        "",                 # estado
        "",                 # meio_pagamento
        "Formulário limpo. Pronto para nova venda."  # resultado
    )