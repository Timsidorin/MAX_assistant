import {ToolButton, Flex, Typography} from "@maxhub/max-ui";
import {FiUser, FiPlus} from "react-icons/fi";
import {NavLink} from "react-router";

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
                gap={8}
                style={{ width: '100%' }}
            >
                <NavLink
                    to='/create'
                    style={{
                        textDecoration: 'none',
                        color: 'inherit',
                        flex: 1,
                        display: 'flex'
                    }}
                >
                    <ToolButton
                        icon={<FiPlus size={24}/>}
                        onClick={() => {}}
                        style={{ width: '100%' }}
                    >
                        <Typography.Action>
                            Создать
                        </Typography.Action>
                    </ToolButton>
                </NavLink>
                <NavLink
                    to='/profile'
                    style={{
                        textDecoration: 'none',
                        color: 'inherit',
                        flex: 1,
                        display: 'flex'
                    }}
                >
                    <ToolButton
                        icon={<FiUser size={24}/>}
                        onClick={() => {}}
                        style={{ width: '100%' }}
                    >
                        <Typography.Action>
                            Профиль
                        </Typography.Action>
                    </ToolButton>
                </NavLink>
            </Flex>
        </div>
    )
}