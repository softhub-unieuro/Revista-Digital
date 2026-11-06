# Testes e critérios de aceite

## Estratégia

Unidade para regras e limites; integração com PostgreSQL, armazenamento e worker;
contratos de API; E2E no navegador com PDF real. Mocks podem isolar falhas, mas não
substituem o teste integrado que comprova persistência e processamento.

Manter CI por alteração e executar a matriz completa na homologação. Guardar comandos,
commit, ambiente, fixtures e evidências. Cobertura percentual sozinha não comprova o produto.

## Casos obrigatórios

| ID | Caso | Resultado verificável |
|---|---|---|
| T01 | Checkout limpo | Frontend, API, banco e worker executam pelos comandos documentados |
| T02 | Migrações | Criar banco do zero e atualizar versão anterior sem perda |
| T03 | Login/logout/CSRF | Credenciais reais, sessão inválida após logout e escrita sem CSRF bloqueada |
| T04 | Perfis/propriedade | Colaborador não publica nem altera dados/arquivos alheios |
| T05 | Admin final | Não desativar/remover o último administrador |
| T06 | Ciclo editorial | Rascunho → publicada → arquivada → rascunho com histórico |
| T07 | Privacidade de arquivo | URL conhecida de rascunho/arquivo antigo não acessível ao público |
| T08 | Catálogo e busca | Combinar ano/tema/termo e retornar contagens reais |
| T09 | Busca consecutiva | Saúde e depois Educação pelo cabeçalho atualizam URL, campo e resultados |
| T10 | Filtro administrativo | Rascunho e busca restringem a lista conjuntamente |
| T11 | Acervo Todos | Exibir todos os anos; ano vazio com mensagem e navegação |
| T12 | Slug/ID inválido | Estado 404, sem mostrar a primeira revista por engano |
| T13 | Upload vazio | Não avançar nem publicar sem arquivo e campos válidos |
| T14 | Limites PDF | 1 e 300 aceitos; 301, inválido, senha e excesso de bytes rejeitados |
| T15 | Processamento | Falha/retry/reinício sem duplicação nem troca indevida do arquivo ativo |
| T16 | Capa | Capa automática/customizada correta e persistente |
| T17 | Range e download | HEAD, 200, 206, 416, conteúdo íntegro e nome de arquivo correto |
| T18 | Leitor responsivo | Todas as páginas acessíveis, em especial 2, 4 e 300 no celular |
| T19 | Animação | Índice consistente sob gestos rápidos e redução de movimento |
| T20 | Zoom | Sem corte de controles e sem conflito de arrasto/deslize |
| T21 | Avaliação | Nota persiste; alterar nota não duplica contagem |
| T22 | Configurações | Opções alteram interface e comportamento do servidor quando aplicável |
| T23 | Persistência | Publicação/usuário/capa/nota permanecem após recarga e reinício |
| T24 | Visual e responsividade | Comparação com referência e sem overflow global em 390 px |
| T25 | Acessibilidade | Foco, rótulos, contraste, teclado e leitura sem animação |
| T26 | Capacidade | Matriz de 300 páginas e orçamento de recursos medidos |
| T27 | Concorrência | Edições simultâneas não sobrescrevem sem aviso; uploads repetidos não duplicam |
| T28 | Recuperação | Restaurar banco e arquivos em ambiente limpo e ler PDF íntegro |
| T29 | Produção | DNS/HTTPS, login, publicação e leitura/download no domínio final |
| T30 | Entrega | Manual executável por outra pessoa e demonstração completa ao administrador |

## Matriz de navegadores e tamanhos

Desktop: Chrome, Firefox, Safari e Edge atuais. Toque: Safari iOS e Chrome Android.
Registrar versões no teste. Viewports mínimos de comparação: 390×844, 768×1024,
1024×768 e 1440×1000. Priorizar dispositivo real no leitor; emulação sozinha não
comprova comportamento de memória e gestos de um celular.

## Jornada E2E de aceite

1. Entrar como administrador e criar categoria e usuário colaborador.
2. Colaborador envia PDF real de 300 páginas e preenche os dados.
3. Verificar processamento, capa e rascunho persistentes; tentativa de publicação é negada.
4. Editor revisa e publica. Público encontra pelo título, tema e ano.
5. Abrir PDF, navegar, ampliar, virar páginas e chegar à última no desktop e celular.
6. Avaliar, recarregar, alterar nota e confirmar média/contagem.
7. Baixar e verificar integridade do PDF; testar a opção de download.
8. Trocar PDF sem quebrar versão vigente; simular falha e repetir.
9. Arquivar e comprovar que consulta/arquivo público deixam de estar disponíveis.
10. Restaurar backup e repetir leitura e acesso administrativo.

## Critério de bloqueio

Não entregar com falha de autenticação/permissão, arquivo privado exposto, perda de
dados, publicação falsa, página inacessível ou incapacidade de abrir o PDF de 300 páginas.
Falha visual ou de acessibilidade que impeça uso do fluxo principal também bloqueia.
Itens menores precisam de responsável e registro explícito, sem ocultar limitações.

## Evidência atual — 04/11/2026

As provas de backend, HTTPS/backup e interface estão em [S03](15-sprint3-entrega.md).
A [consolidação](18-homologacao-leitor.md) acrescenta 54 testes backend/5 Node,
concorrência editorial sem sobrescrita, rede simulada, uploads/Range concorrentes,
arquivo próximo de 200 MiB e páginas mistas/rotacionadas em 390 px. T27 de conflito
editorial está coberto em duas conexões e duas abas. T26 continua parcial por falta
de heap/carga de leitores/aparelhos. T24/T25/T29/T30 ainda dependem dos aceites,
dispositivos e ambiente final descritos nos relatórios; não considerar T03–T30 todos
aprovados pela existência de um build ou de um pacote Docker.
