import {Flex, CellSimple, Button, Typography, IconButton} from "@maxhub/max-ui";
import {StepNumber} from "@components/sendReportPage/StepNumber.jsx";
import {postTicket} from "@api/ticket.js";
import {useParams} from "react-router";
import { FiArrowLeft } from "react-icons/fi";

export function ListStepsContainer() {
    const steps = [
        'Поисковым агентом ищем email для связи',
        'Генерируем текст письма с помощью гигачата',
        'Заполняем шаблон официального заявления',
        'Прикладываем фото',
        'Отправляем'
    ];
    let params = useParams();

    return (
        <>
            <IconButton
                appearance="themed"
                aria-label="Название кнопки"
                mode="primary"
                size="medium"
                style={{position: 'absolute', left: '16px', top: '16px'}}
            >
                <FiArrowLeft size={24} />
            </IconButton>
            <ListStepsView steps={steps} uuid={params.uuid}/>
        </>
    )
}

function ListStepsView(props) {
    return (
        <>
            <Flex align='center' style={{marginTop: '40%'}} direction='column' gap={8}>
                <Typography.Headline style={{marginBottom: '5%'}}>
                    Отправка заявления
                </Typography.Headline>
                {props.steps.map((step, index) => {
                    return (
                        <CellSimple
                            before={<StepNumber step={index + 1}/>}
                            height="compact"
                            title={step}
                            key={index}
                            style={{
                                backgroundColor: 'rgba(225,225,225,0.25)',
                                border: '1px solid rgba(225,225,225,1)',
                                borderRadius: '8px',
                            }}
                        />
                    );
                })
                }
            </Flex>
            <Button style={{marginTop: '24px'}} stretched onClick={async () => {
                await postTicket(props.uuid)
            }}>
                Отправить заявление
            </Button>
        </>
    )
}