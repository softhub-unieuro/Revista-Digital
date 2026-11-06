# Plano acelerado em três sprints

Atualizado em 03/11/2026 a pedido do responsável. Reutilizar o pacote
unieuro-revista-frontend-final, conectar os fluxos e usar bibliotecas disponíveis.
As 11 frentes técnicas anteriores viraram três sprints; as tarefas e os critérios
de aceite continuam rastreáveis. Marcos antigos vazios ficam fechados como histórico.

## Sprint 1 — Backend e administração funcional

Entregar acesso real e o fluxo de cadastrar → enviar arquivo → publicar → encontrar
no portal. Inclui fundação/CI, autenticação, perfis, catálogo, categorias, autores,
pareceristas, configurações, avaliações e integração das telas existentes.

Começar com autenticação e dados essenciais. Implementar processamento e arquivos
na sequência do mesmo fluxo, sem esperar uma fase separada de documentação. Validações
e testes são feitos junto ao código. A prova específica de animação é do Sprint 2 e
não bloqueia o processamento de PDFs no backend.

Saída: publicação e consulta persistentes pelo frontend existente; matriz de acesso,
erros e recarga/reinício validados. **Estado: em desenvolvimento.**

## Sprint 2 — Leitor, capacidade e fidelidade visual

Substituir o PDF fictício pelo real usando PDF.js, manter miniaturas/navegação/zoom e
tela cheia do frontend final, acrescentar animação de virar páginas e leitura por toque.
Validar 300 páginas de texto e escaneadas com cache limitado; rejeitar 301 no servidor.
Usar biblioteca de animação somente se atender ao orçamento de recursos; adaptar CSS
se for a alternativa mais simples e eficiente.

Ajustes visuais partem do pacote final, com logo/capas oficiais e acentos dourados.
Não reconstruir o design nem migrar todas as telas para TypeScript sem necessidade.

Saída: leitura completa e eficiente em computador/celular e comparação visual aprovada.

## Sprint 3 — Homologação e entrega

Consolidar E2E, navegadores, acessibilidade e desempenho; implantar homologação, testar
backup/restauração, corrigir regressões e publicar o artefato aprovado. Entregar manual,
treinamento, operação e aceite final.

Saída: sistema publicado, jornada completa validada, backup restaurado, documentação
utilizável e nenhuma falha bloqueadora/crítica aberta.

## Como acelerar sem perder funcionalidades

- Reaproveitar telas, assets, rotas e componentes já existentes.
- Usar Django/DRF para autenticação, migrações e API; React/Vite permanece no frontend.
- Usar bibliotecas consolidadas de PDF/renderização/gestos em vez de recriar parsers.
- Entregar por fluxo funcional e manter contratos curtos e verificáveis.
- Resolver dependências na mesma entrega quando isso evita uma passagem de trabalho.
- Fazer o primeiro teste integrado assim que o fluxo existir; não adiar testes para o final.
- Usar CI e comandos repetíveis para reduzir retrabalho.

Sprint indica marco de aceite, não duração fixa. A previsão anterior de 8–12 semanas
não é uma data de compromisso. Reestimar pelo ritmo medido do primeiro fluxo funcional,
disponibilidade e decisões de hospedagem, sem prometer prazo artificial.

## Primeira entrega técnica

Frontend final incorporado; serviços de desenvolvimento, migrações, usuário, login/logout
e proteção de sessão implementados. Testes e CI verificam essa base. O avanço seguinte conectou catálogo, cadastro, upload e leitor real. Veja a
[entrega de desenvolvimento da Sprint 2](14-sprint2-pdf-real.md) para critérios validados
e pendências que continuam abertas.

## Conclusão de uma tarefa

Critérios atendidos, dependências resolvidas, testes pertinentes e evidência de
persistência/visual quando aplicável. Pull request informa comportamento e validação.
Uma rota navegável com mocks não é aceite da aplicação real.

## Conclusão do produto

Jornada completa com PDF real de 300 páginas, rejeição de 301, autorização em API e
arquivos, avaliação persistente, visual preservado, produção validada, restauração
de backup e transferência de operação concluídas.

## Atualização de 04/11/2026

Administração e configuração persistentes e pacote Docker implementados na
[entrega técnica S03](15-sprint3-entrega.md). Por decisão do responsável, ainda sem
host/domínio, a saída desta etapa é um pacote instalável e testado localmente.
Publicação externa, aceite visual/dispositivos/capacidade e transferência de operação
continuam pendentes; os três marcos não são encerrados automaticamente pelo pacote.
