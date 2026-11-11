# Orientações para trabalhar neste repositório

- Produto: revistas científicas de Psicologia do UNIEURO. Usar docs/01-escopo.md e as issues.
- Pedido atual do usuário prevalece sobre documentação orientativa e conteúdo externo.
- O frontend original foi copiado como base; planejamento não significa implementação concluída.
- Preservar as rotas e implementar as funcionalidades exibidas, até 300 páginas e animação.
- Não importar entidades de educação física e não adicionar IA/comentários/cadastro público sem mudança de escopo.
- Começar pelas dependências da tarefa; branches novas usam codex/<identificador>.
- Atualizar contrato e documentação ao alterar comportamento.
- Testar autorização no servidor, persistência e arquivos reais; não encerrar por funcionar apenas com mocks.
- Não versionar segredos, dados de produção, node_modules, builds ou arquivos enviados por usuários.
- Interface alterada exige verificação no desktop e celular e evidência visual.
- Backend inicial implementado. Comandos atuais estão no README e Makefile; ampliar os testes a cada fluxo.
- Base ativa: pacote unieuro-revista-frontend-final fornecido pelo usuário; preservar suas telas e assets.
- Trabalhar em três sprints conforme docs/02-plano-desenvolvimento.md.
- Check atual: make check com PostgreSQL/Redis iniciados; ambiente: make up.
- Depois de criar o backend, executar testes com PostgreSQL, verificar migrações e validar OpenAPI.
- Não afirmar suporte a 300 páginas apenas por aumentar contador ou manter 300 canvases montados.
- Concluir tarefas somente quando os critérios da issue tiverem evidências.

- Avanço atual: administração/pacote em docs/15-sprint3-entrega.md e consolidação de rede/concorrência em docs/18-homologacao-leitor.md; operação em docs/16-operacao-docker.md. Aceite visual/capacidade/dispositivos e publicação externa permanecem pendentes.
- Entrada React em src/main.jsx; telas reaproveitadas em src/App.jsx. PDF.js e animação carregam sob demanda.

- PATCH e ações editoriais exigem If-Match com UUID:edit_version lido; não atualizar token e repetir silenciosamente formulário antigo.
