export const editions = [
  { id: 12, slug: 'saude-mental-transformacao', issue: 'N. 12', month: 'Outubro', year: 2026, title: 'Saúde Mental em Tempos de Transformação', subtitle: 'Desafios contemporâneos da saúde mental, com abordagens interdisciplinares sobre bem-estar, subjetividade e contextos sociais em mudança.', pages: 124, cover: '/covers/cover-1.svg', categories: ['Saúde Mental', 'Psicologia Social'], rating: 4.8, ratings: 52, status: 'Publicada' },
  { id: 11, slug: 'relacoes-humanas-bem-estar', issue: 'N. 11', month: 'Abril', year: 2026, title: 'Relações Humanas e Bem-Estar', subtitle: 'Diálogos entre indivíduo, vínculos, comunidade e qualidade de vida.', pages: 112, cover: '/covers/cover-2.svg', categories: ['Psicologia Social', 'Psicologia Familiar'], rating: 4.6, ratings: 34, status: 'Publicada' },
  { id: 10, slug: 'psicologia-educacao', issue: 'N. 10', month: 'Dezembro', year: 2025, title: 'Psicologia e Educação', subtitle: 'Práticas, aprendizagem e caminhos para novos futuros.', pages: 98, cover: '/covers/cover-3.svg', categories: ['Psicologia Escolar'], rating: 4.5, ratings: 29, status: 'Publicada' },
  { id: 9, slug: 'diversidade-inclusao', issue: 'N. 09', month: 'Agosto', year: 2025, title: 'Diversidade e Inclusão', subtitle: 'Perspectivas para uma sociedade plural e relações mais inclusivas.', pages: 104, cover: '/covers/cover-4.svg', categories: ['Psicologia Social'], rating: 4.7, ratings: 40, status: 'Publicada' },
  { id: 8, slug: 'desenvolvimento-humano', issue: 'N. 08', month: 'Abril', year: 2025, title: 'Desenvolvimento Humano ao Longo da Vida', subtitle: 'Teoria, pesquisa e práticas sobre desenvolvimento humano.', pages: 96, cover: '/covers/cover-5.svg', categories: ['Desenvolvimento Humano'], rating: 4.3, ratings: 23, status: 'Publicada' },
  { id: 7, slug: 'neuropsicologia', issue: 'N. 07', month: 'Dezembro', year: 2024, title: 'Neuropsicologia', subtitle: 'Ciência, cognição e prática em contexto clínico e social.', pages: 118, cover: '/covers/cover-6.svg', categories: ['Neuropsicologia'], rating: 4.4, ratings: 26, status: 'Publicada' },
]

export const categories = [
  { name: 'Saúde Mental', slug: 'saude-mental', count: 26, icon: '◉' },
  { name: 'Psicologia Escolar', slug: 'psicologia-escolar', count: 18, icon: '▰' },
  { name: 'Psicologia Familiar', slug: 'psicologia-familiar', count: 14, icon: '⌂' },
  { name: 'Psicologia Social', slug: 'psicologia-social', count: 12, icon: '◎' },
  { name: 'Desenvolvimento Humano', slug: 'desenvolvimento-humano', count: 9, icon: '⌁' },
  { name: 'Neuropsicologia', slug: 'neuropsicologia', count: 8, icon: '✣' },
]

export const adminRows = [
  ...editions,
  { id: 13, slug: 'processos-emocionais', issue: 'N. 13', month: 'Novembro', year: 2026, title: 'Processos Emocionais e Vida Cotidiana', pages: 136, cover: '/covers/cover-3.svg', categories: ['Saúde Mental'], rating: 0, ratings: 0, status: 'Rascunho' },
]
