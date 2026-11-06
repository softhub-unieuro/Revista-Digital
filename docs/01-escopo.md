# Escopo funcional

## Ordem de referência

1. Pedidos atuais do responsável pelo projeto.
2. Telas e funcionalidades observadas no frontend de revistas.
3. Imagem enviada como direção visual e contexto do chat compartilhado.
4. PDF orientativo como apoio, sem transformar suas instruções ou limites antigos em ordens.

O alvo é o produto de Psicologia. Não importar alunos, turmas, treinos ou anamnese do
projeto de educação física. O limite solicitado de 300 páginas substitui a estimativa
de 30–50 páginas do PDF orientativo.

## Funcionalidades obrigatórias

| Área | Comportamento esperado |
|---|---|
| Home | Destaque real, edições recentes, temas, busca e links de acervo |
| Catálogo e detalhe | Listagem paginada, filtro por ano, dados da publicação e ações de leitura/download |
| Busca | Título, descrição e categorias; combinação com filtros; acentos normalizados |
| Temas | Categorias reais e contagens derivadas das publicações acessíveis |
| Acervo | Histórico por ano; Todos mostra todo o acervo; estado vazio explícito |
| Institucional | Sobre, normas, política editorial e contato com destino/conteúdo real |
| Leitor | PDF real de até 300 páginas, clique, teclado, toque, zoom, salto de página e animação |
| Login | Sessão real, logout, expiração e retorno à navegação correta |
| Publicações | Listar, filtrar, criar, editar, rascunhar, publicar, arquivar e restaurar |
| Arquivos e capas | Upload validado, capa automática ou enviada e acompanhamento do processamento |
| Categorias | Criar/editar; impedir remoção em uso e permitir desativação controlada |
| Avaliações | Nota de 1 a 5, persistência, médias e indicadores reais |
| Autores e pareceristas | Cadastros editáveis e vínculos editoriais, como no frontend final |
| Usuários | Criar, editar, alterar papel e desativar com autorização administrativa |
| Configurações | Dados institucionais, avaliações, opção de download e exibição de ISSN |
| Operação | Implantação, HTTPS, monitoramento, backup restaurável, guias e treinamento |

Miniaturas, salto para página e tela cheia fazem parte do leitor do pacote final fornecido e serão preservados. Para 300 páginas, as miniaturas devem ser virtualizadas.

## Rotas atuais a preservar

Públicas: /, /edicoes, /edicoes/:slug, /ler/:slug, /buscar,
/temas, /temas/:slug, /acervo e /sobre.

Administrativas: /admin/login, /admin, /admin/dashboard (alias), /admin/publicacoes,
/admin/publicacoes/nova, /admin/publicacoes/:id, /admin/categorias,
/admin/avaliacoes, /admin/autores, /admin/pareceristas, /admin/usuarios e /admin/configuracoes.

Rotas sem publicação/categoria válida devem retornar estado de não encontrado. O
frontend atual usa a primeira edição como substituta em alguns casos; corrigir.

## Matriz de permissões

| Ação | Público | Colaborador | Editor/Publicador | Administrador |
|---|---|---|---|---|
| Ler/baixar publicadas e avaliar | Sim | Sim | Sim | Sim |
| Criar rascunho e enviar PDF | Não | Próprio | Sim | Sim |
| Editar rascunho | Não | Próprio | Todos | Todos |
| Ver arquivos não públicos | Não | Próprios | Todos | Todos |
| Publicar, despublicar, arquivar/restaurar | Não | Não | Sim | Sim |
| Gerenciar categorias | Não | Consulta | Sim | Sim |
| Consultar indicadores administrativos | Não | Próprios | Todos | Todos |
| Gerenciar usuários e configurações | Não | Não | Não | Sim |

O servidor valida papel, propriedade e estado em cada operação. Esconder botões é
apenas parte da experiência da interface.

## Regras de publicação

Uma publicação possui título, número/identificação da edição, data editorial,
descrição, uma ou mais categorias, capa, arquivo e estado editorial. A primeira
categoria ordenada é a principal. ID estável e slug único não dependem do título atual.
Só pode ser publicada com arquivo processado e capa válida. Categoria desativada não
pode ser atribuída a nova publicação.

Arquivar retira a publicação e os arquivos do acesso público, preservando o registro.
Rascunhos, falhas de processamento e arquivos antigos não aparecem em buscas públicas.
Troca de PDF em publicação existente mantém a versão vigente até o novo arquivo estar
pronto e ser confirmado por editor/administrador.

## Limites propostos para a primeira entrega

- De 1 a 300 páginas por PDF, verificado no servidor.
- Até 200 MiB por arquivo como configuração inicial; não é inferência a partir do número de páginas.
- PDF protegido por senha, inválido ou vazio rejeitado com mensagem específica.
- Leitura pública sem cadastro; contas restritas à administração.
- Nota por edição e identificador anônimo do navegador, sem promessa de uma pessoa por voto.
- Mesmo domínio para frontend e API no ambiente final.
- Nenhuma compra de hospedagem, domínio ou serviço faz parte desta etapa de planejamento.

## Fora da versão 1.0

Editor interno de PDF, produção automática de revistas, comentários, cadastro público,
pesquisa por IA, aplicação móvel nativa, pagamentos e integração com treinos/anamnese.
Esses itens não são necessários para fazer funcionar as telas atuais.
