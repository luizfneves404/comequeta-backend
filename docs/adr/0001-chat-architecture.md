# ADR 0001 — Arquitetura do chat (SCRUM-66)

- **Status:** Aceito
- **Contexto:** Épico "Comé que Tá?" — US06 (SCRUM-8): usuários precisam trocar
  mensagens 1:1. Projeto acadêmico, app mobile (Capacitor) + backend FastAPI.

## Decisão

Chat **1:1** com entrega em **tempo real via WebSocket** servido pelo próprio
backend FastAPI, com **persistência das mensagens no banco** e **histórico via
REST**. Autenticação reaproveita o **JWT** já existente.

Dois aparelhos não se comunicam diretamente: o backend é o ponto de relay e a
fonte de verdade do histórico. Cada cliente mantém um **cache local on-device**
(ver ADR 0003), mas o servidor é necessário para entregar a mensagem ao outro
usuário.

### Modelo de dados

`messages`:

| campo | tipo | observação |
|-------|------|------------|
| id | int (PK) | |
| sender_id | int (FK users) | |
| recipient_id | int (FK users) | |
| content | text | conteúdo textual da mensagem |
| created_at | datetime (UTC) | preenchido pelo servidor |
| read_at | datetime nullable | marca de leitura |

Índice por `(sender_id, recipient_id, created_at)` para paginar conversas.

### Contrato de API (fonte única para frontend e backend)

REST (todos exigem `Authorization: Bearer <jwt>`):

- `GET /chat/conversations` → lista de interlocutores com a última mensagem e a
  contagem de não-lidas:
  `[{ peer_id, peer_name, last_message, last_at, unread }]`
- `GET /chat/messages/{peer_id}?before=<iso>&limit=<n>` → histórico (mais
  recentes primeiro), paginação por `before` (cursor temporal):
  `[{ id, sender_id, recipient_id, content, created_at, read_at }]`
- `POST /chat/messages` body `{ recipient_id, content }` → persiste, entrega via
  WebSocket aos sockets abertos do destinatário, e devolve a mensagem criada.
- `POST /chat/messages/{peer_id}/read` → marca como lidas as mensagens recebidas
  daquele interlocutor.

WebSocket:

- `GET /ws/chat?token=<jwt>` → o servidor valida o JWT, registra a conexão pelo
  `user_id` e mantém um mapa `user_id -> conexões`.
- Frames JSON do cliente para o servidor:
  `{ "type": "message", "recipient_id": <int>, "content": "<str>" }`
- Frames do servidor para o cliente:
  `{ "type": "message", "message": { ...Message } }` (entrega em tempo real,
  tanto para o destinatário quanto eco para o remetente).

O `POST /chat/messages` e o envio via WS convergem para o mesmo caso de uso
(`SendMessage`), garantindo que toda mensagem seja persistida e entregue.

## Consequências

- **Tempo real** sem polling; conexão única por cliente.
- **Limite conhecido:** uma única instância do backend mantém as conexões em
  memória. Para escalar horizontalmente seria preciso um **pub/sub (ex.: Redis)**
  para propagar mensagens entre instâncias — fora do escopo do MVP acadêmico
  (ver ADR 0002).
- Segurança: o JWT autentica a conexão; o caso de uso valida que o remetente é o
  usuário autenticado e que o destinatário existe.

## Alternativas consideradas

- **Polling REST** (sem WebSocket): mais simples, porém com latência e desperdício
  de requisições. Mantido como plano B caso o WebSocket traga complexidade de
  hospedagem (ver ADR 0002).
- **Serviço de terceiros (Firebase/Stream)**: rápido, mas adiciona dependência
  externa e foge do objetivo didático de implementar a stack.
