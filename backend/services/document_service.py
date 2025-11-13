# backend/services/document_service.py

"""
Document Service для создания Word документов по шаблону и конвертации в PDF.
"""

import io
import os
import tempfile
from datetime import datetime
from typing import Optional, Tuple
from docxtpl import DocxTemplate
from pathlib import Path


class DocumentService:
    """Сервис для создания Word/PDF документов из шаблона."""

    def __init__(self):
        project_root = Path(__file__).parent.parent.parent
        self.template_path = project_root / "Шаблон заявления.docx"

    def create_complaint_document(
            self,
            city: str,
            street: str,
            organization_name: str,
            person_name: str,
            count_photos: int,
            year: Optional[int] = None,
            convert_to_pdf: bool = True
    ) -> Tuple[bytes, str]:
        """Создает документ по шаблону и конвертирует в PDF."""

        doc = DocxTemplate(str(self.template_path))
        now = datetime.now()
        if year is None:
            year = now.year

        context = {
            'administration_name': organization_name,
            'person': person_name,
            'city': city,
            'street': street,
            'yeer': str(year)[2:],
            'count_photos': count_photos,
            'day_report': now.strftime('%d'),
            'month_report': self._get_month_name_genitive(now.month)
        }
        doc.render(context)

        docx_bytes_io = io.BytesIO()
        doc.save(docx_bytes_io)
        docx_bytes_io.seek(0)
        docx_bytes = docx_bytes_io.getvalue()
        # Конвертация в PDF
        if convert_to_pdf:
            try:
                pdf_bytes = self._convert_to_pdf(docx_bytes)
                return pdf_bytes, 'pdf'
            except Exception as e:
                return docx_bytes, 'docx'

        return docx_bytes, 'docx'

    def _convert_to_pdf(self, docx_bytes: bytes) -> bytes:
        """Конвертирует Word в PDF."""
        try:
            from docx2pdf import convert
        except ImportError:
            raise ImportError("docx2pdf not installed. Install: pip install docx2pdf")

        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_docx:
            temp_docx.write(docx_bytes)
            temp_docx_path = temp_docx.name

        temp_pdf_path = temp_docx_path.replace('.docx', '.pdf')

        try:
            convert(temp_docx_path, temp_pdf_path)

            with open(temp_pdf_path, 'rb') as f:
                pdf_bytes = f.read()

            return pdf_bytes

        finally:
            if os.path.exists(temp_docx_path):
                os.remove(temp_docx_path)
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)

    def _get_month_name_genitive(self, month: int) -> str:
        """Возвращает название месяца в родительном падеже."""
        months = {
            1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
            5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
            9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
        }
        return months.get(month, '')



