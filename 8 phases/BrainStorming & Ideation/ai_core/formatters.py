from io import BytesIO
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Inches, Pt

from fpdf import FPDF

from ai_core.assets import ensure_logo_assets
from ai_core.generator import iter_clean_lines, split_terms


def _safe_pdf_text(text: str) -> str:
    """
    Convert text to characters that can be safely written by
    the default PDF fonts.
    """
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.encode("latin-1", "replace").decode("latin-1")


def _set_docx_font(document: Document):
    """
    Set the main DOCX font to Times New Roman.
    """

    styles = document.styles

    normal_style = styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(11)

    for section in document.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)


def _add_docx_footer(document: Document):
    """
    Add a simple footer to the DOCX document.
    """

    for section in document.sections:
        footer = section.footer

        paragraph = footer.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        run = paragraph.add_run(
            "LegalEase - AI Legal Document Generator | Draft for Review"
        )

        run.font.name = "Times New Roman"
        run.font.size = Pt(8)


def format_docx(
    text: str,
    doc_type: str,
    terms: str = "",
    logo_path: str | Path | None = None,
) -> bytes:
    """
    Create a formatted DOCX file and return it as bytes.
    """

    assets = ensure_logo_assets()

    if logo_path is None:
        logo_path = assets["logo"]

    document = Document()

    _set_docx_font(document)
    _add_docx_footer(document)

    # Logo
    if Path(logo_path).exists():
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        run = paragraph.add_run()
        run.add_picture(str(logo_path), width=Inches(3.0))

    # Title
    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    title_run = title.add_run(doc_type.upper())
    title_run.bold = True
    title_run.font.name = "Times New Roman"
    title_run.font.size = Pt(18)

    # Document body
    for line in iter_clean_lines(text):
        paragraph = document.add_paragraph()

        run = paragraph.add_run(line)
        run.font.name = "Times New Roman"
        run.font.size = Pt(11)

        paragraph.paragraph_format.space_after = Pt(6)
        paragraph.paragraph_format.line_spacing = 1.15

    # Key terms table
    term_list = split_terms(terms)

    if term_list:
        document.add_paragraph()

        heading = document.add_paragraph()
        heading_run = heading.add_run("KEY TERMS")
        heading_run.bold = True
        heading_run.font.name = "Times New Roman"
        heading_run.font.size = Pt(12)

        table = document.add_table(
            rows=1,
            cols=2,
        )

        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Table Grid"

        header_cells = table.rows[0].cells
        header_cells[0].text = "Term"
        header_cells[1].text = "Details"

        for term in term_list:
            row = table.add_row()
            cells = row.cells

            if ":" in term:
                name, value = term.split(":", 1)
                cells[0].text = name.strip()
                cells[1].text = value.strip()
            else:
                cells[0].text = term
                cells[1].text = ""

        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.name = "Times New Roman"
                        run.font.size = Pt(10)

    output = BytesIO()
    document.save(output)

    return output.getvalue()


class LegalEasePDF(FPDF):
    """
    Custom PDF class for LegalEase.
    """

    def __init__(self, logo_path: str | Path | None = None):
        super().__init__()

        self.logo_path = str(logo_path) if logo_path else None

        self.set_auto_page_break(
            auto=True,
            margin=18,
        )

    def header(self):
        if self.logo_path and Path(self.logo_path).exists():
            try:
                self.image(
                    self.logo_path,
                    x=75,
                    y=8,
                    w=60,
                )
                self.ln(25)
            except Exception:
                self.ln(8)
        else:
            self.ln(8)

        self.set_font("Times", "B", 9)
        self.cell(
            0,
            6,
            "LegalEase - AI Legal Document Generator",
            align="C",
        )

        self.ln(5)

    def footer(self):
        self.set_y(-15)

        self.set_font("Times", "", 8)

        self.cell(
            0,
            10,
            f"Page {self.page_no()} | Draft for Review",
            align="C",
        )


def format_pdf(
    text: str,
    doc_type: str,
    terms: str = "",
    logo_path: str | Path | None = None,
) -> bytes:
    """
    Create a formatted PDF file and return it as bytes.
    """

    assets = ensure_logo_assets()

    if logo_path is None:
        logo_path = assets["logo"]

    pdf = LegalEasePDF(logo_path=logo_path)

    pdf.add_page()

    # Document title
    pdf.set_font("Times", "B", 16)

    pdf.cell(
        0,
        12,
        _safe_pdf_text(doc_type.upper()),
        align="C",
    )

    pdf.ln(10)

    # Body
    pdf.set_font("Times", "", 11)

    for line in iter_clean_lines(text):
        safe_line = _safe_pdf_text(line)

        pdf.multi_cell(
            pdf.epw,
            6,
            safe_line,
        )

        pdf.ln(2)

    # Key terms
    term_list = split_terms(terms)

    if term_list:
        pdf.ln(4)

        pdf.set_font("Times", "B", 12)

        pdf.cell(
            0,
            8,
            "KEY TERMS",
        )

        pdf.ln(8)

        pdf.set_font("Times", "", 10)

        for term in term_list:
            safe_term = _safe_pdf_text(term)

            pdf.multi_cell(
                pdf.epw,
                5,
                "- " + safe_term,
            )

            pdf.ln(1)

    result = pdf.output()

    if isinstance(result, str):
        return result.encode("latin-1")

    return bytes(result)


def format_html_preview(text: str, doc_type: str) -> str:
    """
    Create an HTML preview for Streamlit.
    """

    import html

    escaped_text = html.escape(text)

    escaped_type = html.escape(doc_type)

    return f"""
    <div style="
        background-color: white;
        color: #111827;
        padding: 40px;
        border-radius: 12px;
        border: 1px solid #d1d5db;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        font-family: Georgia, 'Times New Roman', serif;
        line-height: 1.7;
    ">

        <h1 style="
            text-align: center;
            font-size: 24px;
            margin-bottom: 30px;
        ">
            {escaped_type}
        </h1>

        <div style="
            white-space: pre-wrap;
            font-size: 16px;
        ">
            {escaped_text}
        </div>

    </div>
    """