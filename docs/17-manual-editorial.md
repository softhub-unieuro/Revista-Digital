# Manual editorial

Versão técnica de 04/11/2026. Utilize o domínio e a conta fornecidos pelo responsável
pela instalação. A entrega atual é um pacote Docker; ainda não existe URL pública final.

## Acesso e perfis

Entre em `/admin/login`. A sessão é restaurada ao recarregar; se expirar, entre novamente.
Na tela de login, **Salvar credenciais neste dispositivo** habilita o preenchimento e
salvamento pelo gerenciador de senhas do navegador. O site não persiste a senha; o
navegador pode pedir confirmação e seu suporte varia. Em dispositivo compartilhado,
deixe a opção desmarcada.
Não há cadastro público. Administrador controla acessos e configurações. Editor gerencia
cadastros editoriais e publica. Colaborador prepara e altera seus próprios rascunhos;
publicação, edição de edições publicadas e acesso a dados de outros usuários dependem
de editor/administrador. A API verifica essas regras mesmo com um link direto.

Em **Usuários**, o administrador cria, edita e desativa contas. O último administrador
ativo não pode ser desativado nem perder seu papel. Senha em branco numa edição mantém
a atual; uma senha nova deve atender às regras exibidas pelo servidor. Autores e
pareceristas são pessoas do conteúdo editorial e não recebem login automaticamente.
Recuperação do primeiro acesso é feita pelo responsável técnico conforme o guia Docker.

## Preparar a revista

Cadastre categorias, autores e pareceristas antes de vincular à edição. Informe nome,
instituição e biografia quando aplicável. E-mails desses cadastros não aparecem na API
pública. Desativar um cadastro impede novas seleções; os vínculos anteriores continuam
preservados. A ordem de seleção de autores/pareceristas define sua apresentação.

Em **Nova publicação**, envie o PDF e aguarde o processamento. São aceitos PDFs
válidos de até **300 páginas e 200 MiB**. Arquivos protegidos por senha, corrompidos ou
acima dos limites são recusados. Um digitalizado sem texto pode ser lido normalmente,
mas a busca textual depende do texto existente no próprio PDF; não há OCR automático.
Se houver falha, confira a mensagem e tente novamente pelo fluxo de reenvio.

Preencha título, número, descrição, data, categorias e créditos. A data inicial segue
o calendário de Brasília. Confira a capa gerada da primeira página ou envie imagem
validada pelo campo de capa. Salve como rascunho para revisar. A prévia privada exige
sessão autorizada e não disponibiliza o rascunho ao público.

## Publicar e manter

Quando o PDF estiver pronto e os dados conferidos, use **Publicar**. Abra a edição no
portal e confirme capa, créditos, número real de páginas e conteúdo. A busca pública,
os temas, anos e indicadores passam a refletir os dados persistidos.

Em **Editar publicação**, salve correções e aguarde a confirmação. Se outra sessão
já tiver alterado a edição, o sistema bloqueia a gravação e mantém seu formulário.
Copie os textos que deseja preservar, use **Carregar versão atual**, compare as mudanças
e só então salve novamente. Substituir um PDF
cria histórico: leitores já abertos conservam a versão de arquivo solicitada. O
**Histórico de arquivos** oferece prévias privadas de versões anteriores e registra
os dados associados; ele não fornece restauração automática de metadados.

**Arquivar** retira a edição do público, inclusive leitura/download por URL conhecida.
O conteúdo e histórico continuam guardados. **Restaurar** devolve a edição ao rascunho; publique novamente quando estiver revisada.
Não use arquivamento como exclusão de dados pessoais ou limpeza de disco.

## Portal e leitor

O visitante encontra edições por busca, tema e ano. **Ler edição** abre o leitor real:
capa isolada e páginas duplas no desktop, uma página na tela estreita, miniaturas,
salto de página, zoom, busca textual e tela cheia. Use botões, teclado ou gesto conforme
o dispositivo. A animação respeita a preferência de movimento reduzido do sistema.
O leitor limita páginas renderizadas; não monta 300 canvases ao abrir um livro.
Após uma falha, **Recarregar PDF** ou a tentativa oferecida pelo leitor retomam a página
e a versão de arquivo atuais. Isso não guarda posição depois de fechar a aba.

Quando habilitada, a avaliação aceita notas de 1 a 5 sem login, guarda a nota por
identificador do navegador e permite alterá-la sem duplicar a contagem. Limpeza de
cookies ou outro navegador cria outro identificador; isso não representa pessoa
verificada. O limite de envio pode pedir uma espera antes de nova tentativa.

## Configurações institucionais

O administrador pode alterar nome, descrição, ISSN válido, normas, política e contato.
Os links do rodapé abrem esse conteúdo em **Sobre**. Configure dados reais antes da
publicação final: conteúdo demonstrativo não deve ser apresentado como política oficial.

As opções de avaliações, downloads e acervo público são persistidas. Desativar downloads
remove o botão e bloqueia a rota de download; a leitura continua permitida. Desativar
acervo público retira também arquivos públicos; o painel e as prévias autorizadas seguem
acessíveis. Para ver alterações feitas em outra aba, recarregue o portal.

Administradores consultam **Histórico de alterações** para ver responsável, registro,
ação e campos alterados. Senhas e conteúdos de campos não são registrados ali.

## Quando houver problema

Leia a mensagem antes de reenviar. Erro de acesso pede novo login ou correção do perfil.
Processamento demorado exige worker disponível; comunique ao responsável técnico o
horário e o identificador do trabalho exibido. Erro no PDF exige conferir o arquivo
original. Não envie senhas em capturas ou pedidos de suporte.

A demonstração com a equipe, aprovação visual, testes em celulares físicos e transferência
de acessos serão realizados quando os responsáveis e o ambiente final estiverem definidos.
