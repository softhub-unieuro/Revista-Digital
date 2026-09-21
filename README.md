# Revista Científica de Psicologia — UNIEURO

Frontend completo do MVP da plataforma de revistas digitais de Psicologia.

## Executar

```bash
npm install
npm run dev
```

Build de produção:

```bash
npm run build
```

## Rotas públicas

- `/` — home
- `/edicoes` — catálogo
- `/edicoes/:slug` — detalhe da edição
- `/ler/:slug` — leitor
- `/buscar` — busca
- `/temas` e `/temas/:slug` — temas
- `/acervo` — histórico
- `/sobre` — institucional

## Rotas administrativas

- `/admin/login`
- `/admin/dashboard`
- `/admin/publicacoes`
- `/admin/publicacoes/nova`
- `/admin/publicacoes/:id`
- `/admin/categorias`
- `/admin/avaliacoes`
- `/admin/usuarios`
- `/admin/configuracoes`

## Escopo

É um frontend navegável com dados mockados e estados locais. O login, upload, PDF real, persistência, banco e API devem ser conectados posteriormente ao backend. O fluxo já considera revistas maiores que 100 páginas e usa paginação/carregamento progressivo como princípio para o leitor final.
