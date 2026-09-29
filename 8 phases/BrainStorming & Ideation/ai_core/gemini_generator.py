from config import GEMINI_API_KEY, GEMINI_MODEL
from ai_core.generator import sanitize_text, split_terms


class GeminiDocumentGenerator:
    """
    Generates legal-document drafts using Google's Gemini API.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = (api_key or GEMINI_API_KEY).strip()
        self.model = model or GEMINI_MODEL

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. "
                "Please add your Gemini API key to the .env file."
            )

        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError(
                "The Google GenAI package is not installed. "
                "Run: pip install -r requirements.txt"
            ) from exc

        self.client = genai.Client(api_key=self.api_key)

    def _build_prompt(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> str:
        """
        Build the prompt sent to Gemini.
        """

        document_type = sanitize_text(document_type)
        parties = sanitize_text(parties)
        dates = sanitize_text(dates)

        term_list = split_terms(terms)

        if term_list:
            formatted_terms = "\n".join(
                f"- {term}" for term in term_list
            )
        else:
            formatted_terms = "- No additional terms were provided."

        return f"""
You are assisting with the drafting of a legal document.

Create a clear, professional DRAFT of the following document:

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

DATES:
{dates}

KEY TERMS:
{formatted_terms}

Drafting requirements:

1. Start with a clear document title.
2. Identify the parties and relevant date information.
3. Include an appropriate introductory section.
4. Create logically organized numbered clauses.
5. Incorporate the supplied key terms accurately.
6. Include relevant general provisions where appropriate.
7. Include signature blocks for the parties.
8. Do not invent important personal information, monetary values,
   dates, addresses, or obligations that were not supplied.
9. If information is missing, use a clear placeholder such as
   [ADDRESS] or [DATE] rather than inventing information.
10. Keep the language professional and easy to edit.
11. Return only the document draft itself.
12. Do not use Markdown code fences.
13. End with a short notice that the document is a draft for
    human/legal review and may need to be adapted to the
    applicable jurisdiction.

The result is a drafting aid and must not be presented as a guarantee
of legal validity.
"""

    def generate(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> str:
        """
        Generate the document using Gemini.
        """

        if not sanitize_text(document_type):
            raise ValueError("Document type is required.")

        prompt = self._build_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            dates=dates,
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Gemini request failed: {exc}"
            ) from exc

        document = getattr(response, "text", None)

        if not document:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return document.strip()