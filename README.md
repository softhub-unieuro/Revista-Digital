# Revista Científica de Psicologia — UNIEURO

Desenvolvimento sobre o frontend final fornecido pelo responsável. As telas, o logo,
as capas e a identidade dourada foram reaproveitados; o projeto não está sendo refeito do zero.

## Entrega atual — pacote Docker da Sprint 3

Frontend final preservado e ligado ao backend real: catálogo, upload/processamento,
publicação/arquivamento, autores, pareceristas, usuários com três perfis, configurações,
avaliações e auditoria. O leitor PDF.js aceita até 300 páginas com páginas duplas,
miniaturas limitadas, zoom, busca, tela cheia e animação. Substituições de PDF preservam
as versões anteriores para não misturar bytes durante a leitura.

Validação local: **54 testes de backend e 5 de navegação/data/erros**, build, lint, tipos,
migrações, OpenAPI e npm audit sem vulnerabilidades. Imagens de produção testadas com
HTTPS, arquivos reais, autorização Nginx, Range e restauração de banco/arquivos em outro
ambiente. [Homologação atual e limites](docs/18-homologacao-leitor.md).

O cliente escolheu receber o pacote Docker porque ainda não tem servidor/domínio.
[Instalação e operação](docs/16-operacao-docker.md) · [Manual editorial](docs/17-manual-editorial.md).
Ainda pendem aceite visual humano, matriz completa de navegadores/celulares físicos,
medições de capacidade/memória e implantação pública com responsáveis definidos.
A entrega técnica não representa aceite final ou lançamento v1.0.0.

Na consolidação da Sprint 3, salvamentos concorrentes passaram a ser bloqueados com
aviso e preservação do formulário. O leitor recupera página/versão após falha de rede.
Foram conferidos uploads concorrentes, arquivo próximo de 200 MiB, Range paralelo,
rede simulada e páginas com tamanhos/rotações diferentes em tela de 390 px.

## Três sprints, com entregas por fluxo

1. **Backend e administração:** acesso, dados, cadastro de revista, upload, publicação e portal ligados à API.
2. **PDF e leitor:** até 300 páginas, navegação, miniaturas, zoom, animação e fidelidade ao frontend pronto.
3. **Homologação e entrega:** jornada completa, capacidade, produção, backup, documentação e treinamento.

O escopo foi mantido e as antigas frentes técnicas foram agrupadas. Trabalhos e testes
avançam juntos, sem esperar uma sprint inteira para validar um fluxo.

[Plano](docs/02-plano-desenvolvimento.md) · [Backlog](docs/03-backlog.md) ·
[Issues](https://github.com/Dj157/revista-psicologia-unieuro/issues) ·
[Sprints](https://github.com/Dj157/revista-psicologia-unieuro/milestones)

## Executar

Requisitos: Docker/Compose. Para ferramentas locais: Python 3.12, uv 0.11.14 e Node 24+.

~~~bash
make up
~~~

No ambiente com Colima:

~~~bash
make COMPOSE="docker --context colima compose" up
~~~

O comando gera segredos locais em .env se ainda não existir e inicia os serviços.
Não modifica nem apaga bancos de outros projetos. Endereços:

- Frontend: http://127.0.0.1:15173
- API liveness: http://127.0.0.1:18000/health/live
- API readiness: http://127.0.0.1:18000/health/ready
- Contrato implementado: http://127.0.0.1:18000/api/v1/schema/

Criar o administrador sem senha padrão no código:

~~~bash
docker compose exec api uv run --frozen python manage.py createsuperuser
~~~

Acrescentar --context colima após docker se esse for o contexto usado. Os campos são
solicitados no terminal. O login do frontend usa esse acesso real.

## Validar

Com PostgreSQL e Redis iniciados:

~~~bash
uv sync --project backend --locked
npm ci --prefix frontend
make check
make schema
docker compose exec api uv run --frozen python manage.py check_worker
~~~

Os testes executam em banco próprio de teste. O último comando comprova o caminho
Redis → worker → PostgreSQL. Para parar, make down. Os volumes são preservados.

## PDFs de teste reproduzíveis

~~~bash
uv run --project backend python scripts/generate_pdf_fixtures.py
~~~

Gera PDFs sintéticos de 1, 2, 299, 300, 301 e um digitalizado de 300 páginas em
/tmp/revista-pdf-fixtures. Não são publicações reais. Envie pelo painel com sua conta
editor/admin. O processamento exige o serviço worker ativo. Não há senha padrão.

## Documentação

[Escopo](docs/01-escopo.md), [arquitetura](docs/04-arquitetura.md),
[contrato planejado](docs/05-api.md), [OpenAPI real](docs/openapi.yaml),
[PDF e leitor](docs/06-pdf-leitor.md), [aceite](docs/07-testes-aceite.md),
[design](docs/08-design.md), [implantação](docs/09-deploy-entrega.md),
[riscos](docs/10-riscos-decisoes.md) e [rastreabilidade](docs/12-rastreabilidade.md).

`compose.yaml` serve para desenvolvimento; `compose.production.yaml` usa imagens de
produção, HTTPS e volumes privados. Siga o guia operacional para configurar certificados
e gerar `.env.production`, depois execute `make prod-up`. Para gerar o ZIP a partir de
um commit limpo: `make package`. O artefato fica em `entregas/` com SHA-256.
