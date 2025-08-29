# LoraMon

Plataforma interna para monitorar sensores LoRaWAN armazenados em PostgreSQL/TimescaleDB. O projeto é dividido em três componentes principais:


- **ETL**: processo que lê uplinks brutos e grava séries temporais normalizadas.
- **API**: backend FastAPI que oferece autenticação, cadastro de ativos e consulta de métricas.
- **Web**: frontend Next.js que consome a API e apresenta dashboards e plantas baixas.

## Visão geral da arquitetura

Os serviços são orquestrados via `docker compose` e cada um roda em um container:

| Serviço | Descrição | Porta padrão |
|---------|-----------|--------------|
| `api`   | FastAPI com rotas para autenticação, catálogo de dispositivos e consulta de séries temporais | 8000 |
| `etl`   | Script Python que converte `raw.uplink` em `ingest.measurement` | – |
| `web`   | Aplicação Next.js/React que serve a interface web | 3000 |
| `nginx` | Proxy reverso opcional para unificar acesso externo | 8900 (HTTP), 8943 (HTTPS) |

O banco PostgreSQL/TimescaleDB é esperado externamente (por exemplo, em outro host ou serviço gerenciado).

## Fluxo de dados

1. **Uplink**: mensagens LoRaWAN são inseridas na tabela `raw.uplink`.
2. **ETL**: o container `etl` busca novos registros, aplica o mapeamento opcional de métricas (`app.metric_map`) e insere valores numéricos em `ingest.measurement`.
3. **Agregação**: políticas de retenção, compressão e `continuous aggregates` (`ingest.cagg_5m` e `ingest.cagg_1h`) otimizam consultas históricas.
4. **API**: serviços REST expõem cadastro de sites, dispositivos, sensores, thresholds e séries temporais.
5. **Web**: o frontend realiza login, exibe dashboards e floorplans com últimos valores.

## Banco de dados

A migração inicial cria os schemas `raw`, `ingest` e `app`, além de aplicar políticas de retenção e agregação contínua. Também é criada uma conta administrativa padrão `admin:admin` (alterar após o primeiro acesso).

Execute a migração com:

```bash
psql "$DATABASE_URL_SYNC" -f db/migrations/001_init.sql
```

Para atualizar um banco existente criado antes desta versão, aplique a migração incremental:

```bash
psql "$DATABASE_URL_SYNC" -f db/migrations/002_metric_map_device_profile_enabled.sql
```

### Atualização manual de bancos existentes

Alternativamente, você pode executar diretamente os comandos:

```sql
ALTER TABLE app.metric_map RENAME COLUMN device_prof TO device_profile;
ALTER TABLE app.metric_map ADD COLUMN enabled boolean NOT NULL DEFAULT true;
```

## API

A API é implementada em FastAPI e inclui middleware de CORS configurável via `ALLOW_ORIGINS`. Autenticação usa JWT (`/api/auth/login`). As principais rotas incluem:

- `/api/sites` – CRUD básico de sites.
- `/api/floorplans` – upload de PDFs e recuperação de imagens renderizadas.
- `/api/devices` e `/api/sensors` – cadastro de dispositivos e sensores.
- `/api/placements` – posicionamento de sensores em plantas.
- `/api/thresholds` – configuração de alertas por sensor.
- `/api/timeseries` – consulta de séries temporais e obtenção de últimos valores por planta.
- `/api/metrics` e `/api/catalog` – estatísticas gerais e catálogos para filtros.
- `/api/sql` – execução controlada de consultas SQL (somente admin).

A variável `SECRET_KEY` define a chave usada para assinar os tokens e `ACCESS_TOKEN_EXPIRE_MINUTES` ajusta a expiração.

## ETL

O script `etl/etl.py` utiliza `DATABASE_URL_SYNC` para conexão síncrona. Ele lê lotes de `raw.uplink`, extrai métricas numéricas do JSON, atualiza `ingest.measurement` e mantém um checkpoint em `ingest.etl_checkpoint`. As variáveis `ETL_BATCH` (tamanho do lote) e `ETL_SLEEP` (intervalo de polling) permitem ajustes finos.

## Frontend Web

A interface foi construída com Next.js 14 e Tailwind CSS. O login salva o token JWT no `localStorage` e redireciona para o dashboard, que oferece filtros por aplicação, dispositivo e métrica, além de gráfico temporal e resumo de sensores ativos. Plantas baixas permitem zoom/pan e exibição dos sensores posicionados.

## Variáveis de ambiente

Crie um `.env` com pelo menos:

```
DATABASE_URL=postgresql://usuario:senha@host:5432/loramon
DATABASE_URL_SYNC=postgresql://usuario:senha@host:5432/loramon
SECRET_KEY=troque-esta-chave
ALLOW_ORIGINS=https://app.exemplo.com,https://outro.exemplo.org
ETL_BATCH=5000
ETL_SLEEP=2.0
FLOORPLAN_DIR=/app/app/static/floorplans
```

Se o PostgreSQL estiver fora do Docker, utilize `host.docker.internal` como host nas URLs.

## Executando localmente

1. Copie `.env.example` para `.env` e ajuste as variáveis.
2. Aplique a migração conforme descrito acima.
3. Inicie os serviços: `docker compose build && docker compose up -d`.
4. Acesse a aplicação web em `http://<host>:3000` ou via Nginx em `http://<host>:8900`.
5. A documentação interativa da API fica disponível em `http://<host>:8000/docs`.

## Estrutura do repositório

```
api/    # Backend FastAPI
etl/    # Script ETL para ingestão de uplinks
web/    # Frontend Next.js
nginx/  # Configuração opcional do proxy reverso
db/     # Migrações SQL
```

## Notas

- Os dados brutos não são deletados automaticamente; políticas de retenção aplicam-se apenas a `ingest.measurement`.
- Revise a conta `admin` criada pela migração e defina credenciais seguras antes de exposição pública.
- Ajuste `ALLOW_ORIGINS` para limitar o acesso da API apenas aos domínios desejados.
