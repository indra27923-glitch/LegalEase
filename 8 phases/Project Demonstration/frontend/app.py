import html
import sys
from pathlib import Path

import requests
import streamlit as st


# ---------------------------------------------------------
# Make the project root available for imports
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from ai_core.assets import ensure_logo_assets
from ai_core.formatters import (
    format_docx,
    format_pdf,
    format_html_preview,
)
from ai_core.generator import split_terms
from config import APP_NAME, BACKEND_URL


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title=APP_NAME,
    page_icon="⚖️",
    layout="wide",
)


# ---------------------------------------------------------
# Create logo files automatically
# ---------------------------------------------------------

assets = ensure_logo_assets()


# ---------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #6b7280;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 600;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    .legal-notice {
        background-color: #fff7ed;
        border: 1px solid #fed7aa;
        padding: 14px;
        border-radius: 8px;
        color: #7c2d12;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .preview-container {
        background-color: white;
        border: 1px solid #d1d5db;
        border-radius: 10px;
        padding: 30px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">⚖️ LegalEase</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "AI-Powered Legal Document Generator"
    "</div>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    if assets["logo"].exists():
        st.image(
            str(assets["logo"]),
            use_container_width=True,
        )

    st.markdown("### About LegalEase")

    st.write(
        """
        LegalEase helps create editable drafts of common
        legal documents using AI.
        """
    )

    st.markdown("---")

    st.markdown("### Supported exports")

    st.write("📄 TXT")
    st.write("📝 DOCX")
    st.write("📕 PDF")

    st.markdown("---")

    st.caption(
        "Generated documents are drafts and should be "
        "reviewed for the applicable jurisdiction."
    )


# ---------------------------------------------------------
# Legal notice
# ---------------------------------------------------------

st.markdown(
    """
    <div class="legal-notice">
        <strong>Important:</strong>
        LegalEase generates document drafts for assistance.
        The output is not a substitute for advice from a
        qualified legal professional and may need to be
        adapted to the applicable jurisdiction.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Input section
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">1. Document Information</div>',
    unsafe_allow_html=True,
)

document_type = st.selectbox(
    "Document Type",
    [
        "Employment Agreement",
        "Lease Agreement",
        "Non-Disclosure Agreement (NDA)",
        "Service Agreement",
        "Freelance Agreement",
        "Partnership Agreement",
        "General Legal Agreement",
    ],
)


parties = st.text_area(
    "Parties",
    placeholder=(
        "Example:\n"
        "Employer: ABC Technologies Pvt. Ltd.\n"
        "Employee: Rahul Kumar"
    ),
    height=120,
)


terms = st.text_area(
    "Key Terms",
    placeholder=(
        "Enter important terms separated by semicolons.\n\n"
        "Example:\n"
        "Salary: ₹50,000 per month; "
        "Notice Period: 30 days; "
        "Working Hours: 9 AM to 6 PM"
    ),
    height=130,
)


dates = st.text_input(
    "Effective Date / Relevant Dates",
    placeholder="Example: 1 October 2026",
)


# ---------------------------------------------------------
# Generate button
# ---------------------------------------------------------

generate_button = st.button(
    "✨ Generate Legal Document",
    type="primary",
    use_container_width=True,
)


if generate_button:

    if not parties.strip():
        st.error("Please enter the parties involved.")

    else:

        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "dates": dates,
        }

        with st.spinner(
            "Generating your legal document..."
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=120,
                )

                if response.status_code == 200:

                    result = response.json()

                    document = result.get(
                        "document",
                        "",
                    )

                    if document:

                        st.session_state["document"] = document
                        st.session_state["document_type"] = (
                            document_type
                        )
                        st.session_state["terms"] = terms
                        st.success(
                            "Document generated successfully!"
                        )

                    else:
                        st.error(
                            "The server returned an empty document."
                        )

                else:

                    try:
                        error_data = response.json()

                        error_message = error_data.get(
                            "detail",
                            response.text,
                        )

                    except Exception:
                        error_message = response.text

                    st.error(
                        f"Generation failed: {error_message}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to the LegalEase backend. "
                    "Please make sure the FastAPI server is running "
                    "on http://127.0.0.1:8000."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The request took too long. "
                    "Please try again."
                )

            except Exception as exc:

                st.error(
                    f"Unexpected error: {exc}"
                )


# ---------------------------------------------------------
# Generated document section
# ---------------------------------------------------------

if "document" in st.session_state:

    st.markdown("---")

    st.markdown(
        '<div class="section-title">'
        "2. Generated Document"
        "</div>",
        unsafe_allow_html=True,
    )

    document_type = st.session_state.get(
        "document_type",
        "Legal Document",
    )

    terms = st.session_state.get(
        "terms",
        "",
    )

    # -----------------------------------------------------
    # Preview
    # -----------------------------------------------------

    st.markdown("### Preview")

    preview_html = format_html_preview(
        st.session_state["document"],
        document_type,
    )

    st.markdown(
        preview_html,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # Editable document
    # -----------------------------------------------------

    st.markdown("### Edit Document")

    edited_document = st.text_area(
        "You can edit the generated document below:",
        value=st.session_state["document"],
        height=600,
        key="edited_document",
    )

    st.session_state["document"] = edited_document

    # -----------------------------------------------------
    # Downloads
    # -----------------------------------------------------

    st.markdown("### Download")

    col1, col2, col3 = st.columns(3)

    # TXT
    with col1:

        txt_data = edited_document.encode(
            "utf-8"
        )

        st.download_button(
            label="📄 Download TXT",
            data=txt_data,
            file_name="LegalEase_Document.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # DOCX
    with col2:

        try:

            docx_data = format_docx(
                text=edited_document,
                doc_type=document_type,
                terms=terms,
                logo_path=assets["logo"],
            )

            st.download_button(
                label="📝 Download DOCX",
                data=docx_data,
                file_name="LegalEase_Document.docx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                use_container_width=True,
            )

        except Exception as exc:

            st.error(
                f"DOCX generation failed: {exc}"
            )

    # PDF
    with col3:

        try:

            pdf_data = format_pdf(
                text=edited_document,
                doc_type=document_type,
                terms=terms,
                logo_path=assets["logo"],
            )

            st.download_button(
                label="📕 Download PDF",
                data=pdf_data,
                file_name="LegalEase_Document.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        except Exception as exc:

            st.error(
                f"PDF generation failed: {exc}"
            )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.markdown("---")

st.caption(
    "LegalEase | AI-Powered Legal Document Generator"
)