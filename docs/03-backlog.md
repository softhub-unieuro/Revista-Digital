# Backlog — três sprints

Acompanhar por [sprints](https://github.com/Dj157/revista-psicologia-unieuro/milestones?state=open)
e [issues](https://github.com/Dj157/revista-psicologia-unieuro/issues).
Os códigos F00–F10 identificam frentes técnicas históricas, não sprints separadas.
Fonte estruturada: [backlog.json](../planning/backlog.json).

[Entrega S03](15-sprint3-entrega.md) e [consolidação da homologação](18-homologacao-leitor.md).
Em andamento significa implementação parcial ou aceite ainda pendente; não é conclusão da sprint.

| Tarefa | Sprint | Prioridade | Entrega | Dependências | Estado |
|---|---|---|---|---|---|
| [BASE-01](https://github.com/Dj157/revista-psicologia-unieuro/issues/1) | S01 | P0 | Preservar o frontend e publicar o planejamento | — | Concluída |
| [FUND-01](https://github.com/Dj157/revista-psicologia-unieuro/issues/2) | S01 | P0 | Organizar ferramentas, versões e ambiente local | BASE-01 | Concluída |
| [FUND-02](https://github.com/Dj157/revista-psicologia-unieuro/issues/3) | S01 | P0 | Criar Django, PostgreSQL e migrações iniciais | FUND-01 | Concluída |
| [FUND-03](https://github.com/Dj157/revista-psicologia-unieuro/issues/4) | S01 | P0 | Ampliar CI e manter contrato OpenAPI verificável | FUND-02 | Concluída |
| [FUND-04](https://github.com/Dj157/revista-psicologia-unieuro/issues/5) | S02 | P0 | Provar PDF.js, animação e limites com 300 páginas | FUND-01 | Em andamento |
| [AUTH-01](https://github.com/Dj157/revista-psicologia-unieuro/issues/6) | S01 | P0 | Implementar login, logout, sessão e CSRF | FUND-02 | Concluída |
| [AUTH-02](https://github.com/Dj157/revista-psicologia-unieuro/issues/7) | S01 | P0 | Aplicar permissões dos três perfis em API e frontend | AUTH-01 | Concluída |
| [AUTH-03](https://github.com/Dj157/revista-psicologia-unieuro/issues/8) | S01 | P1 | Gerenciar usuários e registrar ações administrativas | AUTH-02 | Concluída |
| [DOM-01](https://github.com/Dj157/revista-psicologia-unieuro/issues/9) | S01 | P1 | Modelar publicações, categorias e estados editoriais | AUTH-02 | Concluída |
| [DOM-02](https://github.com/Dj157/revista-psicologia-unieuro/issues/10) | S01 | P1 | Implementar catálogo, busca, temas, acervo e destaque | DOM-01 | Concluída |
| [DOM-03](https://github.com/Dj157/revista-psicologia-unieuro/issues/11) | S01 | P1 | Implementar configurações, indicadores e avaliações | DOM-01 | Concluída |
| [PDF-01](https://github.com/Dj157/revista-psicologia-unieuro/issues/12) | S01 | P0 | Receber e validar arquivos PDF de até 300 páginas | DOM-01 | Concluída |
| [PDF-02](https://github.com/Dj157/revista-psicologia-unieuro/issues/13) | S01 | P0 | Processar PDFs em worker com estado e repetição segura | PDF-01 | Concluída |
| [PDF-03](https://github.com/Dj157/revista-psicologia-unieuro/issues/14) | S01 | P0 | Gerenciar capas e armazenamento persistente | PDF-02 | Concluída |
| [PDF-04](https://github.com/Dj157/revista-psicologia-unieuro/issues/15) | S01 | P0 | Servir leitura e download com HTTP Range | PDF-03, AUTH-02 | Concluída |
| [INT-01](https://github.com/Dj157/revista-psicologia-unieuro/issues/16) | S01 | P1 | Conectar páginas públicas e corrigir a busca | DOM-02, DOM-03, PDF-04 | Concluída |
| [INT-02](https://github.com/Dj157/revista-psicologia-unieuro/issues/17) | S01 | P1 | Conectar upload, publicação e edição administrativa | PDF-04, AUTH-02 | Em andamento |
| [INT-03](https://github.com/Dj157/revista-psicologia-unieuro/issues/18) | S01 | P1 | Conectar usuários, categorias, configurações e indicadores | AUTH-03, DOM-03 | Concluída |
| [INT-04](https://github.com/Dj157/revista-psicologia-unieuro/issues/19) | S01 | P1 | Persistir avaliações e controlar disponibilidade | DOM-03, INT-01 | Concluída |
| [READ-01](https://github.com/Dj157/revista-psicologia-unieuro/issues/20) | S02 | P0 | Renderizar PDF real com PDF.js e cache limitado | FUND-04, PDF-04 | Em andamento |
| [READ-02](https://github.com/Dj157/revista-psicologia-unieuro/issues/21) | S02 | P0 | Corrigir paginação responsiva e navegação por toque | READ-01 | Em andamento |
| [READ-03](https://github.com/Dj157/revista-psicologia-unieuro/issues/22) | S02 | P0 | Implementar animação de virar páginas | READ-02, FUND-04 | Em andamento |
| [READ-04](https://github.com/Dj157/revista-psicologia-unieuro/issues/23) | S02 | P1 | Concluir zoom, controles e acessibilidade do leitor | READ-02 | Em andamento |
| [VIS-01](https://github.com/Dj157/revista-psicologia-unieuro/issues/24) | S02 | P1 | Consolidar referência, logo, capas e tokens visuais | BASE-01 | Em andamento |
| [VIS-02](https://github.com/Dj157/revista-psicologia-unieuro/issues/25) | S02 | P1 | Ajustar páginas públicas à imagem de referência | VIS-01, INT-01 | Em andamento |
| [VIS-03](https://github.com/Dj157/revista-psicologia-unieuro/issues/26) | S02 | P1 | Padronizar admin e responsividade | VIS-01, INT-02, INT-03 | Em andamento |
| [QA-01](https://github.com/Dj157/revista-psicologia-unieuro/issues/27) | S03 | P0 | Consolidar testes de API, permissões e persistência | INT-02, INT-03, INT-04 | Concluída |
| [QA-02](https://github.com/Dj157/revista-psicologia-unieuro/issues/28) | S03 | P0 | Executar E2E do fluxo completo e regressões | QA-01, READ-03, READ-04, VIS-03 | Em andamento |
| [QA-03](https://github.com/Dj157/revista-psicologia-unieuro/issues/29) | S03 | P0 | Medir 300 páginas, rede, memória e concorrência | READ-03, PDF-04 | Em andamento |
| [QA-04](https://github.com/Dj157/revista-psicologia-unieuro/issues/30) | S03 | P0 | Verificar acessibilidade e navegadores de entrega | VIS-02, VIS-03, READ-04 | Em andamento |
| [OPS-01](https://github.com/Dj157/revista-psicologia-unieuro/issues/31) | S03 | P0 | Preparar contêineres, HTTPS e homologação | QA-01 | Concluída |
| [OPS-02](https://github.com/Dj157/revista-psicologia-unieuro/issues/32) | S03 | P0 | Implantar backup, restauração e observabilidade | OPS-01 | Em andamento |
| [OPS-03](https://github.com/Dj157/revista-psicologia-unieuro/issues/33) | S03 | P0 | Homologar o candidato à versão 1.0 | QA-02, QA-03, QA-04, OPS-02 | Em andamento |
| [REL-01](https://github.com/Dj157/revista-psicologia-unieuro/issues/34) | S03 | P0 | Publicar a versão 1.0 e verificar produção | OPS-03 | Pendente |
| [REL-02](https://github.com/Dj157/revista-psicologia-unieuro/issues/35) | S03 | P1 | Entregar manuais e treinar a administração | OPS-03 | Em andamento |
| [REL-03](https://github.com/Dj157/revista-psicologia-unieuro/issues/36) | S03 | P0 | Concluir aceite final e estabilização | REL-01, REL-02 | Em andamento |

## BASE-01 — Preservar o frontend e publicar o planejamento

Criar uma base independente e rastreável do projeto de revistas.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/1

- [x] Copiar os 16 arquivos rastreados do frontend sem alterar seus conteúdos e registrar SHA-256.
- [x] Publicar escopo, fases, arquitetura, contratos, testes e checklist de entrega.
- [x] Criar tarefas com dependências e critérios de aceite; validar o build da cópia.

## FUND-01 — Organizar ferramentas, versões e ambiente local

Padronizar o monorepo para execução consistente.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/2

- [ ] Fixar versões compatíveis e lockfiles; separar desenvolvimento e produção.
- [ ] Documentar comandos reais e exemplos de ambiente sem segredos.
- [ ] Executar frontend, API, banco e worker a partir de um checkout limpo.
- [ ] Corrigir os dois achados high do npm audit na base (vite e source-map-js), atualizar o lockfile e repetir build/audit sem regressão.

## FUND-02 — Criar Django, PostgreSQL e migrações iniciais

Construir o backend específico de revistas.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/3

- [ ] Criar projeto Django/DRF com configurações por ambiente e usuário próprio desde a primeira migração.
- [ ] Criar migrações versionadas e validar criação do banco do zero e atualização.
- [ ] Expor liveness/readiness; não importar entidades do sistema de educação física.

## FUND-03 — Ampliar CI e manter contrato OpenAPI verificável

Detectar regressões em cada mudança.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/4

- [ ] Executar lint, build frontend, testes backend com PostgreSQL e verificação de migrações no CI.
- [ ] Gerar e validar o schema OpenAPI; sincronizar contratos e documentação.
- [ ] Aplicar verificações a pull requests sem exigir segredos de produção.

## FUND-04 — Provar PDF.js, animação e limites com 300 páginas

Resolver cedo o risco de desempenho e compatibilidade do leitor.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/5

- [ ] Usar PDFs reais de texto e escaneados com 300 páginas; medir tempo, canvases e memória.
- [ ] Comparar StPageFlip isolado por adaptador com animação CSS de reserva, sem montar 300 canvases.
- [ ] Registrar decisão, versões, orçamento de recursos e arquivos de teste reproduzíveis.

## AUTH-01 — Implementar login, logout, sessão e CSRF

Substituir o login demonstrativo por autenticação real.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/6

- [ ] Validar credenciais no servidor, rotacionar sessão no login e invalidá-la no logout.
- [ ] Proteger login e operações de escrita com CSRF; cookies apropriados para HTTPS.
- [ ] Limitar tentativas e apresentar erro genérico; remover credenciais preenchidas na interface.

## AUTH-02 — Aplicar permissões dos três perfis em API e frontend

Aplicar a matriz de acesso sem depender da visibilidade de botões.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/7

- [ ] Administrador gerencia tudo; editor publica; colaborador altera apenas seus rascunhos.
- [ ] Testar acessos diretos, IDs de outros usuários e arquivos de rascunhos.
- [ ] Restaurar sessão ao recarregar e tratar expiração com retorno à tela adequada.

## AUTH-03 — Gerenciar usuários e registrar ações administrativas

Fazer funcionar a área de usuários já existente.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/8

- [ ] Criar, editar e desativar usuários; controlar papéis somente pelo administrador.
- [ ] Impedir remoção/desativação do último administrador e escalada de privilégios.
- [ ] Auditar mudanças relevantes e documentar criação/recuperação do acesso inicial sem senha no repositório.

## DOM-01 — Modelar publicações, categorias e estados editoriais

Persistir o catálogo e o fluxo editorial.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/9

- [ ] Implementar modelos, constraints, relacionamentos, slugs únicos e categorias ordenadas.
- [ ] Separar estado editorial de processamento do arquivo; só publicar arquivo pronto.
- [ ] Arquivar/restaurar sem perder histórico e preservar a versão publicada durante substituição do PDF.
- [ ] Representar autores e pareceristas como dados editoriais, separados das contas de acesso, sem inventar fluxo complexo de revisão.

## DOM-02 — Implementar catálogo, busca, temas, acervo e destaque

Atender às páginas públicas com dados reais.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/10

- [ ] Listar somente publicadas, com paginação, busca sem diferença de acentos e filtros combináveis.
- [ ] Retornar anos, contagens por categoria e destaque calculados a partir do banco.
- [ ] Retornar 404 para slug inexistente; Todos reúne o acervo inteiro e anos vazios têm estado explícito.

## DOM-03 — Implementar configurações, indicadores e avaliações

Substituir indicadores e configurações fixos.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/11

- [ ] Persistir dados institucionais e opções de avaliações, download e ISSN.
- [ ] Gerar indicadores e médias agregadas reais com consultas controladas.
- [ ] Registrar nota de 1 a 5 por identificador anônimo emitido pelo servidor e edição, com atualização sem duplicar contagem.

## PDF-01 — Receber e validar arquivos PDF de até 300 páginas

Aceitar arquivos reais sem confiar apenas na extensão ou no frontend.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/12

- [x] Receber em streaming para arquivo temporário; limite inicial configurável de 200 MiB.
- [x] Validar assinatura, parse, integridade e quantidade de páginas: 1 e 300 aceitos, 301 rejeitado.
- [x] Rejeitar arquivos inválidos, protegidos por senha e acima do limite; limpar temporários e retornar erro útil.

## PDF-02 — Processar PDFs em worker com estado e repetição segura

Tirar processamento pesado do ciclo HTTP.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/13

- [x] Registrar job durável e estados queued, processing, ready e failed.
- [x] Gerar metadados/capa com limites de tempo e recursos, erro rastreável e retomada após reinício.
- [x] Aplicar idempotência, versionamento e repetição sem duplicar publicação nem substituir arquivo vigente por falha.

## PDF-03 — Gerenciar capas e armazenamento persistente

Manter arquivos e capas disponíveis entre implantações.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/14

- [ ] Usar diretório privado em volume persistente e identificadores gerados pelo servidor.
- [ ] Gerar capa da primeira página ou aceitar imagem validada, corrigindo orientação e dimensões.
- [ ] Remover órfãos com política de retenção e registrar arquivos/derivados em backup.

## PDF-04 — Servir leitura e download com HTTP Range

Entregar arquivos extensos sem carregá-los na memória da API.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/15

- [ ] Autorizar cada acesso antes de delegar ao Nginx em localização interna.
- [ ] Testar 200, HEAD, Range 206, Content-Range, 416 e nomes de download.
- [ ] Bloquear arquivos de rascunhos/arquivados ao público, inclusive por URL conhecida; aplicar opção de download sem prometer DRM.

## INT-01 — Conectar páginas públicas e corrigir a busca

Trocar arrays demonstrativos por respostas da API.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/16

- [x] Criar cliente de API, estados de carregamento, vazio, erro e cancelamento.
- [x] Ligar home, catálogo, detalhe, temas, acervo e busca; sincronizar URL e campo em buscas consecutivas.
- [x] Corrigir Todos, slugs inválidos e contagens; não importar mocks em caminhos de produção.

## INT-02 — Conectar upload, publicação e edição administrativa

Concluir o fluxo administrativo principal.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/17

- [ ] Bloquear avanço sem arquivo/informações válidas; mostrar progresso e estado do processamento.
- [ ] Ligar capa, rascunho, publicar, salvar, arquivar e restaurar com confirmação de resultado.
- [ ] Tratar timeout, reenvio, erro do servidor e troca de PDF sem duplicações.

## INT-03 — Conectar usuários, categorias, configurações e indicadores

Fazer funcionar as demais telas do admin.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/18

- [ ] Implementar ações reais de criar/editar e persistir opções com feedback de erro/sucesso.
- [ ] Aplicar filtro de status e busca combinados, paginação e números reais.
- [ ] Exibir menus e ações por perfil sem substituir a verificação no servidor.
- [ ] Conectar Autores e Pareceristas do frontend final com cadastros reais, vínculos e contagens; preservar suas rotas.

## INT-04 — Persistir avaliações e controlar disponibilidade

Manter nota e média consistentes após recarregar.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/19

- [ ] Enviar nota real, recuperar a nota do navegador e atualizar média/contagem após sucesso.
- [ ] Tratar opção de avaliações desativadas, repetição, indisponibilidade e limitação de requisições.
- [ ] Testar alteração da nota sem nova contagem e leitura pública sem login.

## READ-01 — Renderizar PDF real com PDF.js e cache limitado

Substituir ReaderPage fictício pelo conteúdo original.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/20

- [ ] Carregar PDF.js e worker compatíveis apenas ao abrir o leitor.
- [ ] Renderizar texto/links e páginas visíveis, cancelar renderizações antigas e liberar canvases.
- [ ] Manter número real de páginas e cache limitado; testar abertura, erro de rede e PDF problemático.

## READ-02 — Corrigir paginação responsiva e navegação por toque

Permitir ler todas as páginas em qualquer dispositivo.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/21

- [ ] No celular avançar uma página; no desktop usar capa isolada e páginas duplas com limites corretos.
- [ ] Implementar clique, teclado e deslize, respeitando interação com zoom e seleção de texto.
- [ ] Testar 1, 2, 299 e 300 páginas e redimensionamento sem perder a página selecionada.

## READ-03 — Implementar animação de virar páginas

Entregar o efeito solicitado mantendo a leitura utilizável.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/22

- [ ] Integrar a solução aprovada no spike por um adaptador isolado do renderizador.
- [ ] Manter índice consistente durante gestos rápidos, mudança de tamanho e troca de documento.
- [ ] Respeitar prefers-reduced-motion e modo sem animação; não renderizar todo o livro para animar.

## READ-04 — Concluir zoom, controles e acessibilidade do leitor

Tornar a leitura de revistas extensas prática e legível.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/23

- [ ] Implementar zoom/ajuste, indicador e salto para página com nomes acessíveis e limites validados.
- [ ] Evitar cortes, saltos de layout e conflitos entre pan, swipe e virar página.
- [ ] Garantir foco visível, teclado, mensagens de erro e alternativa de leitura sem animação.
- [ ] Preservar miniaturas e tela cheia do frontend final; virtualizar miniaturas para 300 páginas.

## VIS-01 — Consolidar referência, logo, capas e tokens visuais

Transformar a imagem e o contexto do chat em critérios verificáveis.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/24

- [ ] Preservar logo oficial e capas já recebidos no pacote final e registrar sua origem.
- [ ] Preservar os acentos dourados do pacote final fornecido pelo responsável.
- [ ] Definir fontes, pesos, cores, espaçamentos e tamanhos de referência com aprovação visual objetiva.

## VIS-02 — Ajustar páginas públicas à imagem de referência

Reproduzir a composição institucional solicitada.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/25

- [ ] Ajustar header, busca, destaque, capas, recentes, temas, acervo e rodapé.
- [ ] Substituir símbolos tipográficos por ícones consistentes e ativar os links institucionais.
- [ ] Comparar capturas em desktop e celular; corrigir overflow de 452 px em viewport de 390 px.

## VIS-03 — Padronizar admin e responsividade

Manter a mesma identidade no fluxo de gestão.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/26

- [ ] Padronizar navegação, tabelas, campos, botões, estados e mensagens.
- [ ] Tornar formulários e tabelas utilizáveis em 390, 768, 1024 e 1440 px.
- [ ] Entregar evidências de comparação e acesso por teclado sem bloquear ações na tela pequena.

## QA-01 — Consolidar testes de API, permissões e persistência

Comprovar os contratos e as regras reais do sistema.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/27

- [ ] Cobrir ciclo editorial, proprietário, CSRF, arquivos privados, categorias e configurações.
- [ ] Testar migrações do zero, erros de processamento e consistência após reinício.
- [ ] Executar no CI com PostgreSQL e arquivos de teste; não usar só mocks para afirmar integração.

## QA-02 — Executar E2E do fluxo completo e regressões

Demonstrar a jornada da publicação até a leitura pública.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/28

- [ ] Login, upload real, processamento, publicar, buscar, ler, avaliar, baixar, editar e arquivar.
- [ ] Reproduzir e fechar os bugs de busca, filtro, Todos, mobile e formulário vazio.
- [ ] Testar persistência após recarga e reinício e guardar capturas/evidências do candidato à entrega.

## QA-03 — Medir 300 páginas, rede, memória e concorrência

Validar capacidade real e limites conhecidos.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/29

- [ ] Executar a matriz de PDF textual e escaneado, 300/301 páginas e 200 MiB.
- [ ] Medir primeira página, troca, quantidade de canvases e crescimento de memória em navegação longa.
- [ ] Testar leituras e uploads simultâneos, reinício do worker e falhas de rede; registrar dispositivo/rede/limitações.

## QA-04 — Verificar acessibilidade e navegadores de entrega

Garantir uso em computador, celular e tablet.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/30

- [ ] Testar Chrome, Firefox, Safari e Edge atuais e toque em Safari iOS/Chrome Android.
- [ ] Verificar foco, nomes acessíveis, contraste, zoom do navegador e redução de movimento.
- [ ] Registrar bugs por severidade; entrega sem bloqueadores ou falhas críticas nos fluxos obrigatórios.

## OPS-01 — Preparar contêineres, HTTPS e homologação

Criar o ambiente semelhante à produção.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/31

- [ ] Separar imagens/processos web, API e worker, mantendo PostgreSQL e arquivos persistentes.
- [ ] Configurar mesmo domínio para frontend/API, TLS, rotas SPA e limites alinhados de upload.
- [ ] Fornecer variáveis por mecanismo de segredos, DEBUG desativado e credenciais iniciais fora do Git.

## OPS-02 — Implantar backup, restauração e observabilidade

Permitir operar e recuperar o sistema.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/32

- [ ] Agendar backup de banco e arquivos fora do host e definir retenção/responsável.
- [ ] Restaurar um ambiente limpo e comprovar publicações, usuários e PDFs íntegros.
- [ ] Expor métricas/health, alertar falhas de worker e armazenamento, definir procedimento de rollback.

## OPS-03 — Homologar o candidato à versão 1.0

Reunir evidências finais no ambiente de entrega.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/33

- [ ] Usar contas de teste por perfil e publicações reais autorizadas, incluindo um PDF de 300 páginas.
- [ ] Registrar aceite dos fluxos e do visual, corrigir regressões e congelar o candidato.
- [ ] Confirmar domínio, hospedagem, responsáveis, capacidade e janela de publicação.

## REL-01 — Publicar a versão 1.0 e verificar produção

Disponibilizar o sistema funcional no ambiente final.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/34

- [ ] Criar tag versionada e implantar o mesmo artefato homologado com migrações controladas.
- [ ] Executar smoke test público e administrativo, leitura/download e verificação dos backups.
- [ ] Reverter de forma documentada se um critério crítico falhar; guardar URL e evidências.

## REL-02 — Entregar manuais e treinar a administração

Permitir uso e manutenção sem depender do autor da implementação.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/35

- [ ] Entregar manual do professor: acesso, upload, capa, categoria, rascunho, publicar e arquivar.
- [ ] Entregar guia técnico de instalação, ambiente, migrações, operação e recuperação.
- [ ] Fazer demonstração com publicação completa e transferir acessos por canal apropriado, sem registrá-los no Git.

## REL-03 — Concluir aceite final e estabilização

Encerrar a entrega com evidências e pendências transparentes.

Issue: https://github.com/Dj157/revista-psicologia-unieuro/issues/36

- [ ] Verificar todos os critérios obrigatórios e rastrear cada tarefa ao seu resultado.
- [ ] Registrar versão, responsável, data, limitações e itens futuros em termo de entrega.
- [ ] Acompanhar a janela de estabilização acordada, resolver bloqueadores e atualizar a documentação.
