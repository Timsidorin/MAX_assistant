import {ButtonNavigation} from "@components/createPage/ButtonNavigation.jsx";
import {Flex} from "@maxhub/max-ui";
import {FiCamera, FiUpload} from "react-icons/fi";
import {WhatIsScanner} from "@components/createPage/WhatIsScanner.jsx";
import {LastedTickedContainer} from "@components/createPage/Ticked/LastedTicked.jsx";
import {useNavigate} from "react-router";

export function CreatePage() {

    const navigate = useNavigate();

    const linkManualCreate = () => {
        navigate("/selected-position");
    };

    return <>
        <Flex direction="column" gap={8}>
            <Flex direction="row" gap={12} style={{width: '100%'}}>
                <ButtonNavigation
                    name='Сканер'
                    icon={<FiCamera size={24}/>}
                    style={{flex: 1}}
                    onAction={linkScanner}
                />
                <ButtonNavigation
                    name='Ручная загрузка'
                    icon={<FiUpload size={24}/>}
                    style={{flex: 1}}
                    onAction={linkManualCreate}
                />
            </Flex>
            <WhatIsScanner />
        </Flex>
        <LastedTickedContainer/>
    </>;
}

function linkScanner() {
    //пока в максе нет доступа к камере и gps делаем так
    window.open(__BASE__SCANNER__URL__ + `?user_id=${window.WebApp.initDataUnsafe.user.id}`);
}