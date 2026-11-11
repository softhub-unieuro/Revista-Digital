"""PDFs sintéticos para QA. Nunca são conteúdo editorial de produção."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

parser = argparse.ArgumentParser()
parser.add_argument(
    "--large",
    action="store_true",
    help="Inclui PDF sintético próximo de 200 MiB para teste de transporte.",
)
parser.add_argument("--output", type=Path, default=Path("/tmp/revista-pdf-fixtures"))
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
for count, scanned in [
    (1, False),
    (2, False),
    (299, False),
    (300, False),
    (301, False),
    (300, True),
]:
    filename = args.output / f"{'scanned' if scanned else 'text'}-{count}.pdf"
    pdf = canvas.Canvas(str(filename), pagesize=(595, 842))
    for number in range(1, count + 1):
        if scanned:
            image = Image.new("RGB", (595, 842), "#fbf8ee")
            draw = ImageDraw.Draw(image)
            draw.rectangle((30, 30, 565, 812), outline="#164565", width=3)
            draw.text(
                (60, 80), f"PDF DIGITALIZADO - TESTE QA\nPagina {number} de {count}", fill="#164565"
            )
            draw.ellipse((120, 180, 470, 530), fill="#c1d5c7")
            draw.rectangle((60, 590, 535, 600), fill="#b39231")
            pdf.drawImage(ImageReader(image), 0, 0, width=595, height=842)
        else:
            pdf.setFillColorRGB(0.98, 0.97, 0.94)
            pdf.rect(0, 0, 595, 842, fill=1, stroke=0)
            pdf.setFillColorRGB(0.04, 0.2, 0.34)
            pdf.setFont("Times-Bold", 28)
            pdf.drawString(50, 755, "Revista de Psicologia")
            pdf.setFont("Helvetica", 14)
            pdf.drawString(50, 715, "UNIEURO - arquivo sintetico para validacao")
            pdf.setFont("Times-Roman", 20)
            pdf.drawString(50, 650, f"Pagina {number} de {count}")
            pdf.setFont("Helvetica", 12)
            pdf.drawString(50, 610, "Saude mental, educacao e desenvolvimento humano.")
            pdf.drawString(50, 570, "Texto selecionavel. Links externos e navegacao interna.")
            pdf.linkURL("https://www.unieuro.edu.br/", (50, 535, 350, 555))
            pdf.drawString(50, 540, "Conheca o UNIEURO")
            pdf.bookmarkPage(f"page{number}")
            if number == 1:
                pdf.linkAbsolute("Ultima pagina", f"page{count}", (50, 490, 350, 515))
                pdf.drawString(50, 495, "Ir para a ultima pagina")
            pdf.setFillColorRGB(0.7, 0.57, 0.19)
            pdf.rect(50, 460, 495, 3, fill=1, stroke=0)
            pdf.setFillColorRGB(0.3, 0.4, 0.5)
            pdf.setFont("Helvetica", 10)
            pdf.drawString(50, 60, "DOCUMENTO DE TESTE - SEM CONTEUDO EDITORIAL")
        pdf.showPage()
    pdf.save()
    print(f"{filename.name}: {filename.stat().st_size} bytes")

# Orientações e tamanhos mistos exercitam viewport/rotação sem imagens gigantes.
filename = args.output / "mixed-300.pdf"
pdf = canvas.Canvas(str(filename))
for number in range(1, 301):
    width, height = (842, 595) if number % 2 == 0 else (595, 842)
    pdf.setPageSize((width, height))
    pdf.setPageRotation(90 if number % 7 == 0 else 0)
    pdf.drawString(40, height - 60, f"Pagina {number} de 300 - tamanhos e rotacoes mistos")
    pdf.showPage()
pdf.save()
print(f"{filename.name}: {filename.stat().st_size} bytes")
if args.large:
    from pypdf import PdfWriter

    # Anexo sem compressão para testar tamanho em disco/transporte, sem alegar
    # que este arquivo reproduza o custo de decodificar 200 MiB de fotografias.
    filename = args.output / "large-200mib.pdf"
    writer = PdfWriter(clone_from=args.output / "text-300.pdf")
    writer.add_attachment("qa-padding.bin", bytes(200 * 1024 * 1024 - 512 * 1024))
    writer.write(filename)
    assert 199 * 1024 * 1024 < filename.stat().st_size <= 200 * 1024 * 1024
    print(f"{filename.name}: {filename.stat().st_size} bytes (anexo sintetico; abaixo de 200 MiB)")
