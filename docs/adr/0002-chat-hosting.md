# ADR 0002 — Hospedagem do chat (SCRUM-67)

- **Status:** Aceito
- **Contexto:** Definir onde/como o chat (WebSocket + REST, ADR 0001) é hospedado.
  Projeto acadêmico, sem orçamento para infraestrutura gerenciada robusta.

## Decisão

O chat roda **no mesmo processo e host do backend** FastAPI. O WebSocket
(`/ws/chat`) e os endpoints REST de chat são servidos pela **mesma aplicação**
(uvicorn), sem serviço separado.

Para o ambiente acadêmico, a aplicação pode ser publicada em qualquer plataforma
que suporte **processos de longa duração com WebSocket** (ex.: Render, Railway,
Fly.io — todas com tier gratuito). **Não** se usa serverless puro (ex.: AWS
Lambda) porque WebSocket exige conexão persistente.

### Requisitos de lançamento (Release Criteria)

- A app sobe com `uvicorn app.main:app` e aceita conexões WebSocket em `/ws/chat`.
- Variáveis sensíveis (`JWT_SECRET_KEY`, `DATABASE_URL`) vêm do ambiente.
- CORS já permite a origem do app (Vite/Capacitor) — ver `app/config.py`.

## Consequências

- Simplicidade máxima para o MVP: um único deploy.
- **Limitação de escala (documentada):** uma instância mantém as conexões em
  memória. Escalar para N instâncias exigiria afinidade de sessão (sticky) ou,
  preferencialmente, **Redis pub/sub** para difundir mensagens entre instâncias.
  Item explicitamente adiado — não é necessário para a entrega acadêmica.
- Se a plataforma escolhida não suportar WebSocket no tier gratuito, o plano B é
  o **polling REST** descrito no ADR 0001 (o contrato REST já cobre envio e
  histórico).
