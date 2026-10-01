# API Security Scanner — Checklist (Fase 1: Scanner CLI)

## Ambiente
- [x] Docker, Python 3.11+, venv configurados
- [x] crAPI a correr localmente (`docker compose up -d`)
- [x] Testes manuais no Postman (login, dashboard, BOLA)

## Script base
- [x] Login via `POST /identity/api/auth/login`, extrair token
- [x] Pedido autenticado com o token (`GET /identity/api/v2/user/dashboard`)

## Checks de segurança
- [x] **Check 1 — Broken Authentication**
- [x] **Check 2 — BOLA / IDOR**
- [x] **Check 3 — Rate Limiting**

## Estrutura do código
- [x] Cada check é uma função, devolve dicionário estruturado
- [x] `run_all_tests()` agrega os resultados
- [x] Relatório final no terminal (`print_report`)
- [x] Relatório completo salvo em JSON (`save_report`)

## Entrega
- [x] README completo (o que faz, como correr, status, disclaimer)
- [x] `report.example.json` incluído no repositório
- [x] `.gitignore` cobre `.venv/`, `report.json`, `.env`, `__pycache__/`, `.DS_Store`
- [x] Commit final + push

## FASE 1 CONCLUÍDA 

---

# Fase 2 
- [ ] Mover credenciais para `.env` em vez de hard-coded
- [ ] Generalizar checks (menos hard-coded ao crAPI especificamente)
- [ ] Embrulhar a lógica num backend FastAPI
- [ ] Guardar resultados em base de dados
- [ ] Frontend React
- [ ] Docker Compose do próprio projeto