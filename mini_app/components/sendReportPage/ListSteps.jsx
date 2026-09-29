import {Flex, CellSimple, Button, Typography, IconButton} from "@maxhub/max-ui";
import {StepNumber} from "@components/sendReportPage/StepNumber.jsx";
import {postTicket} from "@api/ticket.js";
import toast from "react-hot-toast";
import {useParams, useNavigate} from "react-router";
import { FiArrowLeft } from "react-icons/fi";
import {PlugLoader} from "@components/sendReportPage/PlugLoader.jsx";
import {useState} from "react";

export function ListStepsContainer() {
    const steps = [
        'Поисковым агентом ищем почту для связи',
        'Генерируем текст письма с помощью ИИ',
        'Заполняем шаблон официального заявления',
        'Прикладываем фото',
        'Отправляем'
    ];
    let params = useParams();
    const [status, setStatus] = useState(false);
    const navigate = useNavigate();

    const postReport = async () => {
        try {
            setStatus(true);
            const response = await postTicket(params.uuid);
            const pointsMap = {low: 10, medium: 20, high: 50, critical: 100};
            const points = pointsMap[response?.data?.priority] || 10;
            toast.success(`🎉 Заявка принята! +${points} очков ямоборца`, {duration: 4000});
            setTimeout(() => navigate('/profile'), 1200);
        } catch (error) {
            console.error(error);
            toast.error('Не удалось отправить заявку');
            setStatus(false);
        }
    };
    return (
        <>
            <IconButton
                appearance="themed"
                mode="primary"
                size="medium"
                style={{position: 'absolute', left: '16px', top: '16px'}}
                onClick={() => {navigate('/create')}}
            >
                <FiArrowLeft size={24} />
            </IconButton>
            <ListStepsView status={status} steps={steps} click={postReport}/>
        </>
    )
}

function ListStepsView(props) {
    return (
        <>
            <Flex align='center' style={{marginTop: '20%'}} direction='column' gap={8}>
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
            <Button style={{marginTop: '24px'}} stretched onClick={() => {
                props.click();
            }}>
                Отправить заявление
            </Button>
            {
                props.status && <PlugLoader />
            }

        </>
    )
}