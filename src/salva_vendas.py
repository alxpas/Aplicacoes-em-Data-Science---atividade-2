import logging as logger
from datetime import datetime
from src.id_transacao import gerar_id_transacao


# variável de módulo que será preenchida via setter
_supabase_client = None

# Inserindo supabase_client, para registrar a venda em BD
def set_supabase_client(client) -> None:
    """Injeta o cliente Supabase no módulo."""
    global _supabase_client
    _supabase_client = client
    logger.info("Supabase client injetado em src.sales")

def salvar_venda(
    id_transacao: str,
    data_venda: str,
    produto: str,
    preco_unitario,
    quantidade,
    nome_cliente: str,
    cidade: str,
    estado: str,
    meio_pagamento: str
):
    """
    Valida campos e insere a venda na tabela 'vendas' do Supabase.
    Retorna (mensagem, novo_id_transacao, data_venda_atualizada).
    """
    try:
        # Validações básicas
        if not all([produto, preco_unitario, quantidade, nome_cliente, cidade, estado, meio_pagamento]):
            logger.warning("Tentativa de salvar venda com campos obrigatórios faltando.")
            return "Erro: Todos os campos obrigatórios devem ser preenchidos.", "", ""

        # Conversões de tipos
        try:
            preco_unitario_val = float(preco_unitario)
        except Exception:
            logger.warning("Preço unitário inválido: %s", preco_unitario)
            return "Erro: Preço unitário inválido.", "", ""

        try:
            quantidade_val = int(quantidade)
        except Exception:
            logger.warning("Quantidade inválida: %s", quantidade)
            return "Erro: Quantidade inválida.", "", ""

        if preco_unitario_val <= 0 or quantidade_val <= 0:
            logger.warning("Preço ou quantidade menor ou igual a zero.")
            return "Erro: Preço e quantidade devem ser maiores que zero.", "", ""

        # Converte data de DD-MM-AA para ISO (YYYY-MM-DD)
        try:
            data_obj = datetime.strptime(data_venda, "%d-%m-%y")
            data_iso = data_obj.strftime("%Y-%m-%dT00:00:00Z")
        except Exception:
            logger.warning("Formato de data inválido: %s", data_venda)
            return "Erro: Data deve estar no formato DD-MM-AA.", "", ""

        # Prepara payload para inserção
        payload = {
            "produto": produto,
            "quantidade": quantidade_val,
            "valor_unitario": round(preco_unitario_val, 2),
            "nome_cliente": nome_cliente,
            "cidade": cidade,
            "estado": estado,
            "meio_pagamento": meio_pagamento,
            "data_venda": data_iso
        }

        # Insere no Supabase
        if _supabase_client is None:
            logger.error("Cliente Supabase não inicializado. Verifique variáveis de ambiente.")
            return "Erro: Conexão com o banco indisponível. Contate o administrador.", "", ""

        try:
            resp = _supabase_client.table("vendas").insert(payload).execute()
            # Verifica resposta conforme supabase-py (padrão: dict com 'data' e 'error')
            if isinstance(resp, dict):
                if resp.get("error"):
                    logger.error("Erro ao inserir no Supabase: %s", resp.get("error"))
                    return "Erro ao inserir no banco de dados.", "", ""
                else:
                    logger.info("Venda inserida no Supabase: %s", id_transacao)
            else:
                # Em algumas versões resp pode ser um objeto com .data e .error
                try:
                    error = getattr(resp, "error", None)
                    if error:
                        logger.error("Erro ao inserir no Supabase: %s", error)
                        return "Erro ao inserir no banco de dados.", "", ""
                    logger.info("Venda inserida no Supabase: %s", id_transacao)
                except Exception:
                    logger.info("Resposta de inserção recebida do Supabase.")
        except Exception as e:
            logger.exception("Exceção ao inserir no Supabase: %s", e)
            return "Erro ao inserir no banco de dados.", "", ""

        # Mensagem de sucesso
        valor_total = round(preco_unitario_val * quantidade_val, 2)
        mensagem = (
            "Venda registrada com sucesso.\n\n"
            f"ID da Transação: {id_transacao}\n"
            f"Cliente: {nome_cliente}\n"
            f"Produto: {produto}\n"
            f"Quantidade: {quantidade_val} unidades\n"
            f"Valor Unitário: R$ {preco_unitario_val:.2f}\n"
            f"Valor Total: R$ {valor_total:.2f}\n"
            f"Data: {data_venda}\n"
            f"Cidade/Estado: {cidade}/{estado}\n"
            f"Meio de Pagamento: {meio_pagamento}"
        )

        novo_id = gerar_id_transacao()
        return mensagem, novo_id, datetime.now().strftime("%d-%m-%y")

    except Exception as e:
        logger.exception("Erro inesperado em salvar_venda: %s", e)
        return f"Erro ao salvar: {e}", "", ""