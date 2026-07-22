from datetime import datetime

def gerar_id_transacao() -> str:
    """Gera um ID único para a transação"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"T{timestamp}"