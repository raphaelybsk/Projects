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
- [ ] **Check 3 — Rate Limiting**

## Estrutura do código
- [x] Cada check é uma função, devolve dicionário estruturado
- [x] `run_all_tests()` agrega os resultados
- [x] Relatório final no terminal (`print_report`)

---

# Fase 2 (posteriormente)
- [ ] Check de Rate Limiting
- [ ] Mover credenciais para `.env` em vez de hard-coded
- [ ] Embrulhar a lógica num backend FastAPI
- [ ] Guardar resultados em base de dados
- [ ] Frontend React
- [ ] Docker Compose do próprio projeto