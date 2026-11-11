# Arquitetura e decisões técnicas

A fundação está implementada: Django/DRF, PostgreSQL, Redis/Celery, usuário, migrações e autenticação. Entidades editoriais e arquivos abaixo continuam planejados.

## Stack escolhida para iniciar

| Camada | Escolha | Motivo |
|---|---|---|
| Interface | React/Vite existente | Preservar as telas revisadas e reduzir reconstrução |
| API | Python 3.12, Django 5.2 LTS e Django REST Framework | CRUD, permissões, migrações e administração |
| Banco | PostgreSQL 17 | Constraints, índices, relacionamentos e consultas agregadas |
| Processamento | Celery e Redis | Trabalhos de PDF fora do ciclo HTTP; jobs persistidos no banco |
| PDF no navegador | PDF.js com worker da mesma versão | Renderização real e carregamento por partes |
| Animação | Adaptador; StPageFlip como candidato | Confirmar em FUND-04; CSS como alternativa de animação |
| Arquivos | Volume privado persistente e Nginx com acesso interno | Servir Range sem expor rascunhos nem carregar PDF inteiro na API |
| Infraestrutura | Contêineres e proxy no mesmo domínio | Sessões, operação e entrega portáveis |

Fixar versões exatas compatíveis na F01; o frontend copiado mantém seu lockfile original.
A série Django 5.2 tem suporte estendido até abril de 2028, conforme a
[página oficial de versões](https://www.djangoproject.com/download/). Não adotar
automaticamente a versão mais nova sem testar compatibilidade.

PostgreSQL 17 consta como suportado na [política oficial de versões](https://www.postgresql.org/support/versioning/).
Fixar o patch usado na implantação e validar atualizações no ambiente de homologação.

Sessões são adequadas ao mesmo contexto de site; operações de escrita precisam de
CSRF, incluindo o login. Referência: [autenticação DRF](https://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication).

PDF.js pode usar requisições parciais conforme os cabeçalhos do servidor. A estratégia
do projeto é medir isso com arquivos reais, sem presumir que todo PDF abrirá com a
mesma latência. Referência: [FAQ oficial PDF.js](https://github.com/mozilla/pdf.js/wiki/Frequently-Asked-Questions).

O [StPageFlip](https://github.com/Nodlik/StPageFlip) será avaliado em uma prova técnica.
A escolha só permanece se permitir cache limitado e paginação consistente com React.
A API de negócio não depende dessa biblioteca.

## Fluxo de execução

~~~mermaid
flowchart TD
  B[Navegador: React e PDF.js] --> N[Nginx: HTTPS e SPA]
  N --> A[Django/DRF: API e autorização]
  A --> P[(PostgreSQL)]
  A --> Q[Redis: fila]
  Q --> W[Worker de PDF]
  W --> P
  W --> F[(Arquivos privados persistentes)]
  A --> I[Redirecionamento interno autorizado]
  I --> F
  F --> N
~~~

O diretório de mídia não possui rota estática pública. A API verifica publicação e
usuário antes da entrega interna. [Nginx internal](https://nginx.org/en/docs/http/ngx_http_core_module.html#internal)
documenta o mecanismo de localização interna. Avaliar a configuração completa com Range
em PDF-04. Armazenamento S3 privado poderá substituir o volume por adaptador se a
hospedagem exigir; esse desenho deverá preservar autorização, Range e backup.

## Entidades e integridade

| Entidade | Campos e regras principais |
|---|---|
| User | UUID, email único, nome, ativo; campo role único; senha gerenciada pelo Django |
| Category | UUID, slug único, nome, descrição, ativo e ordem |
| Publication | UUID, slug único, título, edição, data editorial, descrição, autor responsável, status e datas |
| PublicationCategory | Publicação, categoria e posição; par único; primeira categoria é principal |
| PublicationFile | UUID, versão, caminho interno, SHA-256, bytes, páginas e estado de processamento |
| CoverAsset | Origem automática/enviada, caminho, tipo, dimensões e relação com versão do PDF |
| ProcessingJob | Arquivo, status, tentativa, timestamps e código de erro; idempotência por versão |
| Rating | Publicação, identificador anônimo derivado, nota 1–5; par único |
| SiteSettings | Registro único versionado de informações e opções institucionais |
| AuditLog | Ator, ação, objeto, data e resumo; não armazenar senha, sessão ou conteúdo dos arquivos |

Criar usuário próprio antes da primeira migração. Adaptar o frontend para IDs como
strings; hoje existem conversões numéricas demonstrativas.

Índices iniciais: status/data editorial, slug único, relação de categorias e data de
publicação. Busca usa título, descrição e categorias, normalizando acentos; planejar
índice compatível com consultas reais após medir planos de execução.

## Estados separados

~~~mermaid
stateDiagram-v2
  [*] --> rascunho
  rascunho --> publicada: editor e arquivo pronto
  publicada --> rascunho: retirar de publicação
  publicada --> arquivada: arquivar
  rascunho --> arquivada: arquivar
  arquivada --> rascunho: restaurar
~~~

Arquivo: queued → processing → ready ou failed. Reprocessar cria nova tentativa
idempotente. Estado editorial não pode ser publicado enquanto o arquivo selecionado
não estiver pronto. Resultado atrasado de job antigo não pode sobrescrever a versão atual.

## Organização prevista do backend

~~~text
backend/
  config/           configurações, URLs e inicialização do worker
  apps/accounts/    usuários, autenticação e permissões
  apps/catalog/     publicações e categorias
  apps/documents/   upload, armazenamento, arquivos e jobs
  apps/ratings/     avaliações e agregados
  apps/site/        configurações e indicadores
  apps/audit/       trilha administrativa
  tests/            integração e contratos
~~~

## Decisões de implementação

- API versionada em /api/v1; administração funcional em /admin no frontend.
- Django admin técnico, se habilitado, em caminho distinto para não colidir com a SPA.
- Paginação de 20 itens, máximo de 100; ordenação explícita.
- Login por sessão HttpOnly/Secure em produção; sem token no localStorage.
- Redis não é fonte de verdade dos jobs; reinício precisa permitir retomada a partir do banco.
- Salvamento e troca de versão são transacionais; publicação exige verificação no servidor.
- Logs com identificador de requisição e mensagens sem credenciais.
- Sem exclusão definitiva de publicações pela interface inicial; arquivar e restaurar.

## Implementação S03 — 04/11/2026

Configuração singleton, pessoas editoriais, créditos ordenados, revisão de publicação
e auditoria com nomes preservados usam PostgreSQL. Revisões referenciam documentos
protegidos contra exclusão; URLs com UUID da versão impedem mistura de Range durante
substituições. Redis limita login/voto atomicamente. Sessão privada ausente retorna 401;
CSRF/negação de perfil retornam 403.

Produção usa React estático em Nginx, Gunicorn e Celery separados; API não root,
volumes privados e X-Accel-Redirect após autorização por requisição. Banco/Redis
sem portas publicadas, TLS obrigatório e migrações antes dos serviços. Backup pausa
escritas para uma cópia coerente e restaura apenas em destino vazio.
Veja [operação](16-operacao-docker.md) e [contrato atual](05-api.md).
