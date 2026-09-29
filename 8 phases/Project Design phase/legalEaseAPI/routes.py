from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ai_core.gemini_generator import GeminiDocumentGenerator


router = APIRouter()


class DocumentRequest(BaseModel):
    document_type: str = Field(
        ...,
        min_length=2,
        description="Type of legal document to generate",
    )

    parties: str = Field(
        ...,
        min_length=2,
        description="Names or details of the parties",
    )

    terms: str = Field(
        default="",
        description="Important terms separated by semicolons",
    )

    dates: str = Field(
        default="",
        description="Relevant dates",
    )


class DocumentResponse(BaseModel):
    document: str


@router.post(
    "/generate",
    response_model=DocumentResponse,
)
def generate_document(request: DocumentRequest):
    """
    Generate a legal-document draft using Gemini.
    """

    try:
        generator = GeminiDocumentGenerator()

        document = generator.generate(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates,
        )

        return DocumentResponse(
            document=document
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {exc}",
        ) from exc