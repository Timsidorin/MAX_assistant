import {Flex, Spinner, Typography} from "@maxhub/max-ui";

export function BaseLoader({style}) {
    return (
        <Flex style={{...style}} align='center' justify='center' direction='column'>
            <Spinner size={40} appearance='themed'/>
            <Typography.Title style={{color: '#2b92ff'}}>
                Загрузка
            </Typography.Title>
        </Flex>
    )
}