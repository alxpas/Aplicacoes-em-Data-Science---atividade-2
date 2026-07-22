import gradio as gr
from datetime import datetime

def build_ui(salvar_venda, limpar_formulario, gerar_id_transacao):
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

    return app
