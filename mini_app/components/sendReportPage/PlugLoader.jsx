import {Spinner} from "@maxhub/max-ui";
import { useEffect, useState } from 'react';

export function PlugLoader() {
    const [currentStep, setCurrentStep] = useState(0);
    const messages = [
        "Ищу канал взаимодействия",
        "Генерирую текст",
        "Заполняю шаблон",
        "Прикладываю фото",
        "Отправляю"
    ];

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentStep(prevStep => {
                const nextStep = prevStep + 1;
                if (nextStep >= messages.length) {
                    clearInterval(interval);
                    return prevStep;
                }
                return nextStep;
            });
        }, 1000);

        return () => clearInterval(interval);
    }, [messages.length]);
    return (
        <div style={
            {
                position: "fixed",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
                backdropFilter: "blur(5px)",
                backgroundColor: "rgba(255, 255, 255, 0.8)",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                zIndex: 1000
            }
        }>
            <Spinner
                appearance="themed"
                size={50}
            />
            {messages[currentStep]}
        </div>
    )
}