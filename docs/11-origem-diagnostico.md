# Origem e diagnóstico da base

Revisão realizada em 03/11/2026.

Origem: [softhub-unieuro/Revista-Digital](https://github.com/softhub-unieuro/Revista-Digital).
Commit de origem: 17ba76c75ffee75c3593d5f7ad962b0854700f7b. Foram copiados 16 arquivos rastreados para
frontend/, preservando conteúdo e registrando SHA-256 em planning/frontend-origem.json.
node_modules, dist e histórico .git da origem não foram importados.

A origem local estava limpa. O outro repositório, educacao-fisica, foi consultado no
levantamento inicial, mas pertence ao EuroHealth 360 e não fornece os modelos deste produto.

## O que foi observado

React/Vite com todas as telas concentradas em src/main.jsx, dados em src/data.js e
CSS em src/styles.css. Seis publicações públicas e um rascunho demonstrativo. Não há
API, persistência nem arquivo PDF real nessa base.

## Falhas reproduzidas

- Login apenas navega para o dashboard; rotas administrativas abrem diretamente.
- Leitor renderiza texto HTML demonstrativo, não o PDF.
- Celular esconde a segunda página e avança de duas em duas: 1 → 3.
- Busca no cabeçalho atualiza a URL, mas mantém resultados da consulta anterior.
- Filtro Rascunho mantém as sete publicações.
- Fluxo chega à revisão sem arquivo ou dados; Publicar não realiza operação.
- Avaliação aparece na tela e some ao recarregar.
- Acervo Todos é um link para o ano 2026; slugs desconhecidos podem mostrar a primeira edição.
- Logo oficial ausente e capas SVG demonstrativas; fontes e proporções diferentes da referência.
- Em 390 px, o documento da home mede 452 px; a grade de temas ultrapassa a largura.
- Links institucionais ainda apontam para âncora vazia.

## Verificação executada na origem

Build de produção aprovado; 18 rotas principais abriram sem erro de console ou overlay.
Catálogo filtrou de seis para uma publicação ao selecionar 2024. Busca inicial funcionou.
Foram exercitados busca consecutiva, filtro administrativo, fluxo vazio de publicação,
avaliação após recarga e leitor mobile. Desktop em 1440×1000; celular em 390×844.

Esses resultados descrevem o protótipo, não comprovam funcionamento do produto final.
O novo repositório executa novamente o build da cópia e publica o resultado do CI.

## Dependências verificadas na cópia

npm ci e npm run build passaram. npm audit registrou dois pacotes com severidade high:
vite e source-map-js. As correções foram incluídas em FUND-01 como trabalho prioritário,
com atualização controlada de versões/lockfile e repetição do build/audit.

A cópia do frontend permanece fiel ao commit de origem; essas correções ainda não foram
implementadas nesta etapa de planejamento. Referências retornadas pelo npm:
[advisory de source-map-js](https://github.com/advisories/GHSA-68fv-2mgg-jv7q) e
[advisory de Vite](https://github.com/advisories/GHSA-698v-4r3x-3vcv).

## Base ativa atualizada pelo responsável

O pacote unieuro-revista-frontend-final foi fornecido após a revisão. Ele substitui a
cópia visual anterior, preservando o logo, capas, cores, componentes e rotas. O manifesto
planning/frontend-final-origem.json registra os hashes recebidos. Alterações sobre essa
base são pontuais: integração de autenticação, configuração de desenvolvimento e ajuste
de largura no celular. Nenhuma reconstrução das telas foi iniciada.

O pacote inclui Autores, Pareceristas, miniaturas e tela cheia. Esses recursos foram
incorporados ao escopo e às tarefas existentes. Os achados do diagnóstico acima referem-se
à base antiga; a autenticação já foi substituída e as dependências atualizadas.
