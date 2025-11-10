import {ToolButton, Typography} from "@maxhub/max-ui";

export function ButtonNavigation(props) {
    return (
        <ToolButton
            onClick={() => {
                props.onAction();
            }}
            appearance="secondary"
            icon={props.icon}
        >
            <Typography.Action>
                {props.name}
            </Typography.Action>
        </ToolButton>
    )
}