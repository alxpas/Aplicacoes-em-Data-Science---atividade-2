from typing import Optional, Tuple, Dict, Any
import os
import logging
from dotenv import load_dotenv
from supabase import create_client, Client

def inicializar_supabase(
    env_path: Optional[str] = None,
    url_keys: Tuple[str, ...] = ("URL_SUPABASE", "SUPABASE_URL"),
    key_keys: Tuple[str, ...] = ("ANON_KEY", "SUPABASE_KEY", "CHAVE_SUPABASE")
) -> Tuple[Optional[Client], str, str, Optional[Dict[str, Any]]]:
    """
    Carrega .env, inicializa cliente Supabase e faz um teste simples de conexão.

    Parâmetros:
    - env_path: caminho para o arquivo .env (se None, usa o padrão do diretório atual).
    - url_keys: nomes alternativos de variáveis de ambiente para a URL do Supabase.
    - key_keys: nomes alternativos de variáveis de ambiente para a chave do Supabase.

    Retorno: (client, status, message, details)
    - client: instância do cliente Supabase ou None se falhou.
    - status: "ok", "warning" ou "error".
    - message: mensagem legível para exibir ao usuário/operador.
    - details: dicionário opcional com informações adicionais (não contém chaves secretas).
    """
    # Carrega .env
    if env_path:
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()

    # Configuração de logging (idempotente)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    logger = logging.getLogger("inicializar_supabase")

    # Lê variáveis de ambiente sem logar valores sensíveis
    supabase_url = None
    supabase_key_present = False
    for name in url_keys:
        val = os.getenv(name)
        if val:
            supabase_url = val
            url_var_name = name
            break

    for name in key_keys:
        val = os.getenv(name)
        if val:
            supabase_key_present = True
            key_var_name = name
            break

    details: Dict[str, Any] = {
        "env_checked": {
            "url_var": url_var_name if supabase_url else None,
            "key_var": key_var_name if supabase_key_present else None
        }
    }

    # Valida presença das variáveis
    if not supabase_url or not supabase_key_present:
        missing = []
        if not supabase_url:
            missing.append("SUPABASE URL")
        if not supabase_key_present:
            missing.append("SUPABASE KEY")
        msg = f"Variáveis de ambiente ausentes: {', '.join(missing)}"
        logger.error(msg)
        return None, "error", msg, details

    # Cria cliente Supabase com tratamento de exceções
    try:
        logger.info("Criando cliente Supabase (variável de URL encontrada em %s).", url_var_name)
        client = create_client(supabase_url, os.getenv(key_var_name))
    except Exception as e:
        logger.exception("Falha ao criar cliente Supabase: %s", e)
        return None, "error", "Falha ao criar cliente Supabase.", {**details, "exception": str(e)}

    # Teste simples de conexão (consulta leve)
    try:
        logger.info("Executando teste de conexão na tabela 'vendas'.")
        resp = client.table("vendas").select("id").limit(1).execute()
        # Verifica formato de resposta do supabase-py
        error = None
        data = None
        if isinstance(resp, dict):
            error = resp.get("error")
            data = resp.get("data")
        else:
            error = getattr(resp, "error", None)
            data = getattr(resp, "data", None)

        if error:
            logger.warning("Cliente criado, mas teste de consulta retornou erro: %s", error)
            return client, "warning", "Cliente criado, mas teste de consulta retornou erro. Verifique permissões/RLS.", {**details, "test_error": str(error)}
        logger.info("Conexão com Supabase estabelecida com sucesso.")
        return client, "ok", "Conexão com Supabase estabelecida com sucesso.", {**details, "test_data_sample": bool(data)}
    except Exception as e:
        logger.warning("Cliente Supabase criado, mas teste de consulta falhou: %s", e)
        return client, "warning", "Cliente criado, mas teste de consulta falhou. Verifique conectividade/permissões.", {**details, "exception": str(e)}
