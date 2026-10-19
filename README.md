# Loja de Sublimação — site completo

Site responsivo com vitrine para clientes e painel administrativo com login.

## Recursos
- Página pública com catálogo, categorias, produtos, preços e campos de personalização.
- Cliente seleciona vários produtos, quantidades, envia observações e pode anexar arte/foto.
- Estimativa de total calculada automaticamente.
- Registro de pedidos em banco SQLite, sem depender de arquivos JSON voláteis.
- Painel com indicadores, consulta de pedidos e atualização de status.
- Administrador pode cadastrar, editar, ocultar e excluir produtos, alterar preços, imagens, categorias e opções de personalização.
- Configurações editáveis: nome da loja, frase, WhatsApp, Instagram, cor, texto inicial, chave Pix e informações de entrega.
- Layout responsivo para celular e computador.

## Rodar no Windows
1. Instale Python 3.10 ou superior: https://www.python.org/downloads/
2. Extraia o ZIP e abra a pasta no VS Code.
3. No terminal, execute:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python app.py
   ```

4. Abra no navegador: http://127.0.0.1:5000
5. Para configurar o administrador, abra: http://127.0.0.1:5000/admin/setup
6. Crie seu próprio usuário e uma senha forte com pelo menos 10 caracteres. Não existe senha padrão.
7. Acesse o painel em: http://127.0.0.1:5000/admin/login

## Banco de dados e arquivos
- O banco local é `loja.db`, criado automaticamente na primeira execução.
- Imagens e arquivos enviados ficam em `static/uploads/`.
- Faça cópias de segurança de `loja.db` e da pasta `static/uploads/`.

## Importante antes de publicar
Esta é uma base funcional para desenvolvimento/local. Para publicar para clientes reais, configure `SECRET_KEY` como variável de ambiente persistente, HTTPS, backups e armazenamento persistente para banco e uploads. Hospedagens efêmeras podem apagar o SQLite e os arquivos enviados após reinicialização/deploy; nesse caso, use PostgreSQL e armazenamento persistente. Não publique o painel sem HTTPS. O site não processa pagamentos automaticamente; o pedido é uma solicitação para confirmar preço final, prazo e entrega.
