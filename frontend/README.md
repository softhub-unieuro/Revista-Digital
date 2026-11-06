# Revista Científica de Psicologia — UNIEURO

Frontend responsivo da plataforma de revistas digitais científicas de Psicologia do Centro Universitário UNIEURO.

## Versão visual

Esta versão usa o logo institucional enviado para o projeto e o design aprovado mais recente:

- interface pública editorial inspirada em catálogo/livraria digital;
- identidade UNIEURO com azul institucional, vermelho como acento e uso contido do dourado no logo;
- títulos editoriais em serif e interface em sans-serif;
- Home com edição em destaque, edições recentes, temas e acervo;
- catálogo com filtros por ano, tema e palavra-chave;
- detalhe da edição;
- leitor com miniaturas, paginação, zoom, download e tela cheia;
- busca, temas e acervo;
- área administrativa com dashboard, publicações, upload em etapas, categorias, avaliações, usuários e configurações.

## Prévia sem instalar

Abra `preview.html` no navegador para visualizar a Home atualizada usando os assets locais da pasta `public/`.

## Executar o app React

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Rotas principais

- `/`
- `/edicoes`
- `/edicoes/:slug`
- `/ler/:slug`
- `/buscar`
- `/temas`
- `/temas/:slug`
- `/acervo`
- `/sobre`
- `/admin/login`
- `/admin`
- `/admin/publicacoes`
- `/admin/publicacoes/nova`
- `/admin/publicacoes/:id`
- `/admin/categorias`
- `/admin/avaliacoes`
- `/admin/usuarios`
- `/admin/configuracoes`

## Identidade visual

- Azul institucional como cor principal.
- Dourado institucional `#B39231`, amostrado do brasão fornecido, para os traços e acentos editoriais.
- O vermelho presente dentro do arquivo oficial do logotipo é preservado como parte da marca.
- Home e painel administrativo seguem as referências visuais aprovadas no chat.
