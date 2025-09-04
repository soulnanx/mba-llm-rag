# Makefile para o projeto de ingestão e busca
.PHONY: help ingest run test-inferencia test-explicita

# Comando padrão
help:
	@echo "Comandos disponíveis:"
	@echo "  help           - Mostra esta mensagem de ajuda"
	@echo "  ingest         - Executa o script de ingestão (ingest.py)"
	@echo "  run            - Executa o chat (chat.py)"
	@echo "  test-inferencia - Testa pergunta que requer inferência"
	@echo "  test-explicita  - Testa pergunta com informação explícita"

# Comando para executar a ingestão
ingest:
	@echo "Executando ingestão..."
	cd src && python ingest.py

# Comando para executar o chat
run:
	@echo "Executando chat..."
	cd src && python chat.py

# Comando para testar pergunta que requer inferência
test-inferencia:
	@echo "Testando pergunta que requer inferência..."
	cd src && source ../venv/bin/activate && echo "Quantos clientes temos em 2024?" | python chat.py

# Comando para testar pergunta com informação explícita
test-explicita:
	@echo "Testando pergunta com informação explícita..."
	cd src && source ../venv/bin/activate && echo "Qual o faturamento da Empresa SuperTechIABrazil?" | python chat.py
