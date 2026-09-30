import {ToolButton, Typography} from "@maxhub/max-ui";

export function ButtonNavigation({name, icon, onAction, className = '', style}) {
    return (
        <div className={`navigation-button-shell ${className}`.trim()} style={style}>
            <ToolButton
                onClick={onAction}
                appearance="secondary"
                icon={icon}
                style={{width: '100%'}}
            >
                <Typography.Action>{name}</Typography.Action>
            </ToolButton>
        </div>
    );
}