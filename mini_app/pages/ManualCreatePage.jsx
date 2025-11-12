import {Flex, Typography} from "@maxhub/max-ui";
import {PhotoListContainer} from "@components/manualCreatePage/PhotoList.jsx";

export function ManualCreatePage() {
    return (
        <>
            <Flex align="center" gapY={100} justify="center" direction='column'>
                <Typography.Headline>Загрузите снимки</Typography.Headline>
                <PhotoListContainer/>
            </Flex>
        </>
    )
}