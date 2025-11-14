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
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")

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
        try:
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

            if convert_to_pdf:
                try:
                    pdf_bytes = self._convert_to_pdf(docx_bytes)
                    return pdf_bytes, 'pdf'
                except Exception as pdf_error:
                    print(f"[Document Service] PDF failed, returning DOCX: {pdf_error}")
                    return docx_bytes, 'docx'
            return docx_bytes, 'docx'
        except Exception as e:
            print(f"[Document Service] Template error: {e}")
            fallback_text = f"""Заявление о дефектах дорожного покрытия

Организация: {organization_name}
Заявитель: {person_name}
Город: {city}
Адрес: {street}
Дата: {datetime.now().strftime('%d %B %Y')}

Описание проблемы: [требует ремонта]

Количество фото: {count_photos}

Подпись: _______________
{person_name}"""
            return fallback_text.encode('utf-8'), 'txt'

    def _convert_to_pdf(self, docx_bytes: bytes) -> bytes:
        """Конвертирует Word в PDF."""
        try:
            from docx2pdf import convert
        except ImportError:
            raise ImportError("docx2pdf not installed")

        temp_docx_path = None
        temp_pdf_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_docx:
                temp_docx_path = temp_docx.name
                temp_docx.write(docx_bytes)
                temp_docx.flush()
            temp_pdf_path = temp_docx_path.replace('.docx', '.pdf')
            print(f"[Document Service] Converting {temp_docx_path} -> {temp_pdf_path}")
            # Удалён аргумент timeout, так как docx2pdf его не поддерживает
            convert(temp_docx_path, temp_pdf_path)

            if not os.path.exists(temp_pdf_path):
                raise FileNotFoundError("PDF not created")

            with open(temp_pdf_path, 'rb') as f:
                pdf_bytes = f.read()

            if len(pdf_bytes) < 1000:
                raise ValueError(f"PDF too small: {len(pdf_bytes)} bytes")

            return pdf_bytes

        finally:
            for path in [temp_docx_path, temp_pdf_path]:
                if path and os.path.exists(path):
                    try:
                        os.unlink(path)
                    except Exception:
                        pass

    def _get_month_name_genitive(self, month: int) -> str:
        months = {
            1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
            5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
            9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
        }
        return months.get(month, '')
