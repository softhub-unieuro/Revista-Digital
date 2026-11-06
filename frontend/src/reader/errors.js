export function readerError(error) {
  if (error.userMessage) return error.userMessage;
  if (error.status === 401)
    return "Seu acesso expirou. Entre novamente para continuar.";
  if (error.status === 403)
    return "Esta edição não está disponível para leitura com o acesso atual.";
  if (error.status === 404)
    return "Esta edição ou versão do PDF não está mais disponível.";
  if (error.name === "PasswordException")
    return "Este PDF exige senha. Solicite uma versão sem proteção à equipe editorial.";
  if (error.name === "InvalidPDFException")
    return "O PDF não pôde ser lido. Informe a equipe editorial para conferir o arquivo.";
  return "Não foi possível carregar o PDF. Confira sua conexão e tente novamente.";
}
