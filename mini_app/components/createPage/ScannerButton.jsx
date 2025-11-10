import { Button, Typography } from "@maxhub/max-ui";
import { useEffect } from "react";
import "@styles/ScannerModal.css";

export function ScannerModal({ isOpen, onClose }) {
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }

        return () => {
            document.body.style.overflow = 'unset';
        };
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <div className="scanner-modal-overlay" onClick={onClose}>
            <div className="scanner-modal-content" onClick={(e) => e.stopPropagation()}>
                <Typography.Title style={{ display: 'block', marginBottom: '30px' }}>
                    Что такое сканер?
                </Typography.Title>

                <Typography.Body style={{ display: 'block', marginBottom: '30px' }}>
                    В <b>MAX</b>, к сожалению, еще не добавили доступ к камере и геоданным.
                    <br/>
                    <span style={{ display: 'block', marginTop: '10px' }}>
                        Мы предлагаем вам открыть сканер отдельной вкладкой, достаточно нажать на кнопку <b>Сканер</b>.
                    </span>
                    <span style={{ display: 'block', marginTop: '10px' }}>
                        После чего - вы сможете в удобной форме сфотографировать дорожные ямы,
                        которые будут <b>классифицированы</b>, также автоматически определится адрес.
                    </span>
                    <span style={{ display: 'block', marginTop: '10px' }}>
                        И, конечно, вы можете воспользоваться <b>Ручной загрузкой</b>,
                        где вручную загрузите фотографии ям и укажите на карте метку, где были произведены снимки.
                    </span>
                </Typography.Body>

                <div style={{ textAlign: 'right' }}>
                    <Button type="primary" onClick={onClose}>
                        Понятно
                    </Button>
                </div>
            </div>
        </div>
    );
}