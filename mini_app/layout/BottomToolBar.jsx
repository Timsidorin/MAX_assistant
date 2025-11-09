import {Button, Flex} from "@maxhub/max-ui";

export function BottomToolBar() {
    return (
        <div style={{
            background: "#edeef2",
            padding: "10px",
            position: "fixed",
            bottom: "0px",
            left: "0px",
            right: "0px",
            width: "100%",
            boxSizing: "border-box",
            zIndex: 1000
        }}>
            <Flex
                direction="row"
                gap={12}
            >
                <Button
                    appearance="neutral"
                    mode="secondary"
                    size="large"
                    stretched
                >
                    Камера
                </Button>
                <Button
                    appearance="neutral"
                    mode="secondary"
                    size="large"
                    stretched
                >
                    Профиль
                </Button>
            </Flex>
        </div>
    )
}