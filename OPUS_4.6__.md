# Walkthrough — Scaffolding + Testes Unitários

## O que foi feito

### Boilerplate do Projeto
Criada toda a estrutura do projeto FastAPI com stubs (interfaces sem implementação):

| Arquivo | Descrição |
|---------|-----------|
| [pyproject.toml](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/pyproject.toml) | Dependências: FastAPI, httpx, redis, SQLAlchemy, pytest, respx, fakeredis |
| [.env.example](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/.env.example) | Template de variáveis de ambiente |
| [docker-compose.yml](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/docker-compose.yml) | FastAPI + Redis 7 + PostgreSQL 16 com healthchecks |
| [Dockerfile](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/Dockerfile) | Python 3.12 slim |
| [V1_IMPLEMENTATION_PLAN.md](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/V1_IMPLEMENTATION_PLAN.md) | Plano de implementação na raiz do projeto |

### Stubs (interfaces para TDD)
Todos os módulos foram criados com **assinaturas completas** e `raise NotImplementedError`:

- [app/clients/glpi.py](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/app/clients/glpi.py) — 7 métodos (init_session, credentials, kill, search, get, create, followup)
- [app/clients/evolution.py](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/app/clients/evolution.py) — 3 métodos (sendText, sendButtons, sendList)
- [app/services/session.py](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/app/services/session.py) — 4 métodos (get, set, delete, update_step)
- [app/services/flow_engine.py](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/app/services/flow_engine.py) — Step enum (8 estados), FlowResult dataclass, process()
- [app/schemas/webhook.py](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/app/schemas/webhook.py) — WebhookPayload com extract_phone() e extract_message()
- [app/schemas/glpi.py](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/app/schemas/glpi.py) — GLPISessionResponse, GLPITicketInput/Response, GLPIFollowupInput
- [app/models/conversation.py](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/app/models/conversation.py) — Tabela conversations (auditoria)

### Testes Unitários (~60 testes)

| Arquivo | Testes | Mock |
|---------|--------|------|
| [test_glpi_client.py](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/tests/unit/test_glpi_client.py) | 17 testes (auth, tickets, headers) | `respx` |
| [test_evolution_client.py](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/tests/unit/test_evolution_client.py) | 9 testes (sendText, buttons, list, headers) | `respx` |
| [test_session.py](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/tests/unit/test_session.py) | 10 testes (get, set, delete, update_step, key) | `fakeredis` |
| [test_flow_engine.py](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/tests/unit/test_flow_engine.py) | 28 testes (8 estados da máquina) | `AsyncMock` |
| [test_webhook.py](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/tests/unit/test_webhook.py) | 12 testes (endpoint + schema extraction) | `TestClient` |

## Como rodar os testes

```bash
# Criar venv e instalar dependências
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
# ou: .venv\Scripts\activate  # Windows

pip install -e ".[dev]"

# Rodar testes
pytest tests/unit/ -v --tb=short
```

> [!NOTE]
> Todos os testes atualmente levantam `NotImplementedError` (via `pytest.raises`). Conforme cada módulo for implementado, os testes devem ser ajustados para verificar o comportamento real.

## Próximos passos
Fase 3 — Implementar os módulos um a um, fazendo os testes passarem:
1. [GLPIClient](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/app/clients/glpi.py#6-71) → testes [test_glpi_client.py](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/tests/unit/test_glpi_client.py) passam
2. [EvolutionClient](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/app/clients/evolution.py#6-54) → testes [test_evolution_client.py](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/tests/unit/test_evolution_client.py) passam
3. [SessionManager](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/app/services/session.py#8-36) → testes [test_session.py](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/tests/unit/test_session.py) passam
4. [FlowEngine](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/app/services/flow_engine.py#29-52) → testes [test_flow_engine.py](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/tests/unit/test_flow_engine.py) passam
5. Webhook handler → testes [test_webhook.py](file:///c:/Users/GuilhermeDeSouza/OneDrive%20-%20UNIMED-CB/%C3%81rea%20de%20Trabalho/middleware/tests/unit/test_webhook.py) passam
