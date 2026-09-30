# API Security Scanner — Checklist (Fase 1: Scanner CLI)

## Ambiente
- [x] Docker, Python 3.11+, venv configurados
- [x] crAPI a correr localmente (`docker compose up -d`)
- [x] Testes manuais no Postman (login, dashboard, BOLA)

## Script base
- [x] Login via `POST /identity/api/auth/login`, extrair token
- [x] Pedido autenticado com o token (`GET /identity/api/v2/user/dashboard`)

## Checks de segurança
- [ ] **Check 1 — Broken Authentication**
  - Repetir pedido ao dashboard sem `headers`
  - Esperado: 401 — se vier 200, reportar vulnerável
- [ ] **Check 2 — BOLA / IDOR**
  - Criar segunda conta de teste (`bubble2`)
  - Obter UUID de um recurso dela (ex.: veículo)
  - Aceder a esse recurso usando o token do primeiro utilizador
  - Esperado: 403/404 — se vier 200, reportar vulnerável
- [ ] **Check 3 — Rate Limiting** (opcional, se sobrar tempo)
  - Enviar 20-30 pedidos seguidos ao login
  - Esperado: bloqueio a partir de X pedidos — se nunca bloquear, reportar vulnerável

## Estrutura do código
- [ ] Transformar cada check numa função (`test_broken_auth()`, `test_bola()`, etc.)
- [ ] Cada função devolve um resultado estruturado: endpoint, esperado, obtido, vulnerável (sim/não)
- [ ] Relatório final no terminal com resumo de todos os checks

## Entrega
- [ ] README do repositório (o que faz, como correr, screenshot do output)
- [ ] Commit final + push

---

# Fase 2 (posteriormente)
- [ ] Embrulhar a lógica num backend FastAPI
- [ ] Guardar resultados em base de dados
- [ ] Frontend React
- [ ] Docker Compose do próprio projeto