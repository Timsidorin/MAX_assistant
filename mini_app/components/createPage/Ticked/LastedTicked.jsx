import {Typography} from "@maxhub/max-ui";
import {TickedCardContainer} from "@components/createPage/Ticked/TickedCard.jsx";

function LastedTickedView(props) {
    return (
        <>
            <Typography.Title>
                Последние заявки
            </Typography.Title>
            <div style={{
                marginTop: "10px",
                display: "flex",
                flexDirection: "row",
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