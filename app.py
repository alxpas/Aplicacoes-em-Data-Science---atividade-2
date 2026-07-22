import os
import logging
from dotenv import load_dotenv

# Funções salvas em /src/web
from src.web.connect_supbase import inicializar_supabase
from src.web.id_transacao import gerar_id_transacao
from src.web.salva_vendas import salvar_venda, set_supabase_client
from src.web.limpa_formulario import limpar_formulario
from src.web.ui import build_ui

# Carrega .env (opcional, a função inicializar_supabase também pode carregar)
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("vendas_app")

# Inicializa Supabase usando a função importada
supabase_client, supabase_status, supabase_message, supabase_details = inicializar_supabase()

# Log do resultado da inicialização e injeção do cliente no módulo de vendas
if supabase_status == "ok":
    set_supabase_client(supabase_client)  # Inserir supabase no módulo src.web.salva_vendas
    logger.info("Supabase inicializado com sucesso: %s", supabase_message)
elif supabase_status == "warning":
    # Ainda injetamos o cliente caso exista, mas registramos o aviso
    if supabase_client is not None:
        set_supabase_client(supabase_client)
    logger.warning("Supabase inicializado com aviso: %s", supabase_message)
else:
    logger.error("Falha ao inicializar Supabase: %s", supabase_message)

# Constrói a interface Gradio passando as funções necessárias
# build_ui deve criar os componentes, registrar os handlers e retornar o objeto Blocks (app)
app = build_ui(salvar_venda, limpar_formulario, gerar_id_transacao)

if __name__ == "__main__":
    # Lança o app Gradio
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        inbrowser=True
    )