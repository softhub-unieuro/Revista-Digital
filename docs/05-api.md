# Contrato implementado da API

Atualizado em 04/11/2026. O contrato completo, campos, enums e respostas estão no
[OpenAPI gerado e validado](openapi.yaml). Base `/api/v1`, sem barra final nas rotas
editoriais. A implementação usa erros DRF (`detail` ou mapa de campos); não usa o
formato de erro envelopado que constava no planejamento inicial.

## Convenções

- UUIDs como strings; datas editoriais `YYYY-MM-DD`; timestamps ISO 8601.
- Listas: `page`, `page_size` (20 padrão, 100 máximo), `count/next/previous/results`.
- Sessão no mesmo domínio; escritas exigem CSRF, inclusive login/avaliação anônima.
- Privado sem sessão: 401; sem permissão ou CSRF inválido: 403. O frontend remove
  sessão expirada ao receber 401 administrativo e restaura o destino após login.
- Objeto inexistente ou não visível: 404. Validação síncrona: 400; limite de upload:
  413; conflito de processamento/estado: 409 conforme endpoint; rate limit: 429;
  Redis indisponível nos limitadores: 503. Consulte respostas específicas no OpenAPI.
- Login: 10 tentativas por identidade derivada de e-mail/IP em 5 minutos. Avaliação:
  30 envios por IP derivado/edição em 5 minutos; `Retry-After` informa espera.

## Rotas públicas

| Método/rota | Comportamento |
|---|---|
| GET /auth/csrf | Cookie/token CSRF |
| POST /auth/login, /auth/logout | Início/fim de sessão |
| GET /auth/me | Usuário atual ou `authenticated:false` |
| GET /public/settings | Conteúdo institucional e opções públicas |
| GET /public/catalog | Total, anos e destaque calculados no banco |
| GET /public/publications | Publicadas; filtros combináveis `q`, `year`, `category` |
| GET /public/publications/{slug} | Detalhe real, créditos, notas e URLs de arquivos |
| GET /public/categories | Categorias ativas e contagens de edições públicas |
| GET/POST /public/publications/{slug}/rating | Nota 1–5 por cookie anônimo assinado; alteração sem nova contagem |
| GET/HEAD /public/publications/{slug}/file | Leitura autorizada, Range 206/416 |
| GET/HEAD /public/publications/{slug}/download | Attachment quando download habilitado |
| GET/HEAD /public/publications/{slug}/cover | Capa autorizada |

Busca usa comparação sem acentos; ano vazio significa todo o acervo. A tela Sobre e os
links de normas/política/contato usam `/public/settings`. Não existem rotas paralelas
`/public/home`, `/public/config`, `/public/pages` ou `/public/archive`.

URLs de PDF incluem `v=UUID_DO_DOCUMENTO`: versões anteriormente publicadas pertencentes
à mesma edição continuam resolvíveis enquanto a edição estiver publicada. Detail aceita
`document=UUID` para seus metadados. Versão desconhecida retorna 404. Arquivamento ou
desativação do acervo bloqueia também URLs conhecidas. Não é URL de armazenamento público.
Desabilitar download não bloqueia leitura nem oferece DRM.

## Rotas privadas

| Método/rota | Permissão/comportamento |
|---|---|
| GET/POST /admin/publications | Colaborador no próprio escopo; editor/admin em todas |
| GET/PATCH /admin/publications/{uuid} | Colaborador apenas próprios rascunhos; editor/admin |
| POST /admin/publications/{uuid}/publish, /archive, /restore | Editor/admin; restore retorna a rascunho |
| GET /admin/publications/{uuid}/revisions | Histórico somente leitura no escopo autorizado |
| POST /admin/uploads | Multipart PDF; 202 com job/documento; máximo 200 MiB |
| GET /admin/jobs/{uuid} | Dono/editor/admin, estado e erro sanitizado |
| POST /admin/jobs/{uuid}/retry | Repetição segura conforme estado/limite |
| POST /admin/jobs/{uuid}/cover | Capa validada, dono/editor/admin e restrições editoriais |
| GET/HEAD /admin/files/{uuid} | Prévia PDF; `kind=cover` para capa; autorização e Range |
| GET/POST /admin/categories; PATCH /admin/categories/{uuid} | Consulta autenticada; escrita editor/admin |
| GET/POST /admin/people; GET/PATCH /admin/people/{uuid} | Autores/pareceristas por `kind`; escrita editor/admin |
| GET/POST /admin/users; GET/PATCH /admin/users/{uuid} | Somente admin; sem exclusão; último admin protegido |
| GET/PATCH /admin/settings | Somente admin; singleton/ISSN validado |
| GET /admin/audit | Somente admin; paginação, snapshots de nomes e campos alterados |

Indicadores e tabelas do frontend usam essas listas/agregados reais; não existem
endpoints separados de dashboard/ratings/unpublish. Vínculos de pessoas usam
`author_ids`/`reviewer_ids`, com tipo e ordem validados. Cadastros inativos podem ser
mantidos em vínculos antigos; novos vínculos são recusados. E-mails editoriais não são
expostos publicamente. Alterações de usuários nunca retornam senha/hash nem aceitam
campos privilegiados como `is_superuser`.

## Processamento e consistência

202 confirma recepção, não aprovação. O worker valida o PDF, rejeita 301 páginas,
proteção por senha e corrupção, gera capa e publica estado pronto/erro. Publicar exige
arquivo pronto. Repetir processamento não duplica publicação. Documentos sem vínculo
podem ser limpos após 30 dias; execução é simulação até receber `--apply`.

Atualizações editoriais bloqueiam a linha da publicação e capturam snapshots na mesma
transação. PATCH e publish/archive/restore exigem `If-Match: "UUID:edit_version"`, com
`edit_version` retornado na última leitura. Token ausente: 428; antigo/inválido: 412.
A conferência ocorre sob bloqueio no banco e uma gravação aceita incrementa a versão.
O frontend preserva o formulário em conflito e exige carregar a versão atual antes de
salvar. O cliente não deve buscar automaticamente um token novo e reenviar um formulário
antigo: primeiro deve revisar/conciliar as alterações. Contrato atualizado na
[consolidação da homologação](18-homologacao-leitor.md).

## Saúde e geração

Fora da base API: `/health/live`, `/health/ready`; esquema em `/api/v1/schema/`.
Execute `make schema` após mudar serializers/views. O CI gera novamente e compara o
arquivo versionado. Nginx entrega PDFs via localização `internal` somente depois da
validação Django; acesso direto à localização protegida é recusado.
