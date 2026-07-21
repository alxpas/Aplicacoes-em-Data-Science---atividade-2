import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import gradio as gr
from typing import Optional

# Funcções salvas em /src
from src.connect_supbase import inicializar_supabase
from src.id_transacao import gerar_id_transacao
from src.salva_vendas import salvar_venda, set_supabase_client
from src.limpa_formulario import limpar_formulario

# Carrega .env (opcional, a função também carrega, mas mantemos para garantir)
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("vendas_app")

# Inicializa Supabase usando a função importada
supabase_client, supabase_status, supabase_message, supabase_details = inicializar_supabase()

# Log do resultado da inicialização
if supabase_status == "ok":
    set_supabase_client(supabase_client) #Inserir supabase no modulo
    logger.info("Supabase inicializado com sucesso: %s", supabase_message)
elif supabase_status == "warning":
    logger.warning("Supabase inicializado com aviso: %s", supabase_message)
else:
    logger.error("Falha ao inicializar Supabase: %s", supabase_message)


# Interface Gradio
with gr.Blocks(title="Registro de Vendas Mobile", theme=gr.themes.Soft()) as app: # type: ignore

    gr.Markdown(
        """
        # Sistema de Registro de Vendas
        ## Acessórios para Smartphones

        Preencha os dados da venda abaixo:
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### Dados da Transação")

            with gr.Row():
                id_transacao = gr.Textbox(
                    label="ID da Transação",
                    value=gerar_id_transacao(),
                    interactive=False,
                    scale=2
                )
                data_venda = gr.Textbox(
                    label="Data da Venda",
                    value=datetime.now().strftime("%d-%m-%y"),
                    placeholder="DD-MM-AA",
                    scale=1
                )

            gr.Markdown("### Dados do Produto")

            produto = gr.Textbox(
                label="Nome do Produto",
                placeholder="Ex: Capinha iPhone 15, Carregador USB-C...",
                lines=1
            )

            with gr.Row():
                preco_unitario = gr.Number(
                    label="Preço Unitário (R$)",
                    placeholder="29.90",
                    minimum=0.01,
                    scale=1
                )
                quantidade = gr.Number(
                    label="Quantidade",
                    placeholder="1",
                    minimum=1,
                    precision=0,
                    scale=1
                )

            gr.Markdown("### Dados do Cliente")

            nome_cliente = gr.Textbox(
                label="Nome do Cliente",
                placeholder="João Silva",
                lines=1
            )

            with gr.Row():
                cidade = gr.Textbox(
                    label="Cidade",
                    placeholder="São Paulo",
                    scale=2
                )
                estado = gr.Dropdown(
                    label="Estado",
                    choices=[
                        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
                        "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
                        "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
                    ],
                    scale=1
                )

            meio_pagamento = gr.Dropdown(
                label="Meio de Pagamento",
                choices=[
                    "Cartão de Crédito", "Cartão de Débito", "PIX",
                    "Dinheiro", "Boleto", "Transferência"
                ]
            )

        with gr.Column(scale=1):
            gr.Markdown("### Dicas")
            gr.Markdown(
                """
                Campos Obrigatórios:
                - Nome do Produto
                - Preço Unitário
                - Quantidade
                - Nome do Cliente
                - Cidade
                - Estado
                - Meio de Pagamento

                Formatos:
                - Data: DD-MM-AA
                - Preço: Use ponto para decimais
                - Quantidade: Apenas números inteiros
                """
            )

    gr.Markdown("---")

    with gr.Row():
        btn_salvar = gr.Button("Registrar Venda", variant="primary", size="lg", scale=2)
        btn_limpar = gr.Button("Limpar Formulário", variant="secondary", size="lg", scale=1)

    with gr.Row():
        resultado = gr.Markdown(label="Resultado", value="Preencha os dados e clique em 'Registrar Venda'")

    # Eventos dos botões
    btn_salvar.click(
        fn=salvar_venda,
        inputs=[id_transacao, data_venda, produto, preco_unitario, quantidade,
                nome_cliente, cidade, estado, meio_pagamento],
        outputs=[resultado, id_transacao, data_venda]
    )

    btn_limpar.click(
        fn=limpar_formulario,
        outputs=[id_transacao, data_venda, produto, preco_unitario, quantidade,
                 nome_cliente, cidade, estado, meio_pagamento, resultado]
    )

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        inbrowser=True
    )