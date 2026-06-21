# ADR 0003 — Banco de dados e armazenamento on-device (SCRUM-21)

- **Status:** Aceito
- **Contexto:** SCRUM-21 pedia "criar instâncias de dev e produção do banco"
  (subtarefas previam AWS RDS/Supabase, VPC, roles, backups). Reavaliado para o
  contexto real: **projeto acadêmico**, app mobile.

## Decisão

Para o MVP acadêmico, **não** provisionamos banco gerenciado na nuvem (AWS
RDS/VPC/roles/backups automáticos). Em vez disso:

1. **Servidor (dados compartilhados — contas e chat):** o backend usa **SQLite**
   (arquivo local), configurável por `DATABASE_URL` (já implementado em
   `app/config.py`/`app/db.py`). É suficiente para a carga do projeto e elimina
   custo/infra. Como o backend depende de SQLAlchemy, migrar para **Postgres**
   no futuro é só trocar a `DATABASE_URL` — sem mudança de código.
2. **Cliente (dados do usuário e cache):** o app **armazena localmente no
   aparelho** o que é específico do usuário e o **cache de mensagens** (histórico
   recente para uso offline), via **Capacitor Preferences** (`@capacitor/preferences`).
   **Uso controlado de armazenamento:** o cache de chat mantém apenas as **N
   mensagens mais recentes por conversa** (ex.: 100) e poda as antigas; o
   histórico completo permanece no servidor e é re-buscado sob demanda.

### Por que o chat ainda precisa do servidor

Mensagens 1:1 entre dois aparelhos não podem ser entregues "só localmente": um
celular não fala direto com o outro. O servidor relaya e guarda a fonte de
verdade (ADR 0001). O armazenamento on-device é **cache/offline**, não
substituto do servidor para a troca de mensagens.

## Mapeamento das subtarefas de SCRUM-21

- **SCRUM-61 (provisionar instância dev/prod):** atendido por SQLite (dev) e
  SQLite no host do backend (prod-acadêmico). Sem RDS.
- **SCRUM-62 (firewall/VPC):** N/A para SQLite local. Em um upgrade para Postgres
  gerenciado, valeria a regra de só aceitar conexões do backend.
- **SCRUM-63 (roles com privilégio mínimo):** N/A para SQLite (arquivo único).
  Documentado para um futuro Postgres: criar `app_user` sem `DROP`/superuser.
- **SCRUM-64 (backups automáticos):** para SQLite, backup = cópia periódica do
  arquivo `.db` (script/cron simples no host). Snapshots gerenciados ficam para
  um eventual Postgres.

## Consequências

- Zero custo de nuvem; setup trivial para o time acadêmico.
- Caminho de evolução claro (trocar `DATABASE_URL` para Postgres) sem reescrever.
- O app ganha resiliência offline para leitura do histórico recente, com tamanho
  de armazenamento limitado por design.
