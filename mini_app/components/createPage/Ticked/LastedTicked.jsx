import {Typography, Flex} from "@maxhub/max-ui";
import {TickedCardContainer} from "@components/createPage/Ticked/TickedCard.jsx";

function LastedTickedView(props) {
    return (
        <>
            <Flex justify='center'>
                <Typography.Title>
                    Последние заявки
                </Typography.Title>
            </Flex>
            <div style={{
                marginTop: "10px",
                display: "flex",
                flexDirection: "column",
                flexWrap: "wrap",
                gap: "10px"
            }}
            >
                <TickedCardContainer/>
            </div>
        </>
    )
}

export function LastedTickedContainer() {
    return (
        <div style={{ marginTop: '20px' }}>
            <LastedTickedView/>
        </div>
    )
}