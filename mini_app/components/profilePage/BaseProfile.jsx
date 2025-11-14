import {
    Container,
    Flex,
    Avatar,
    Typography,
    Panel,
} from "@maxhub/max-ui";
import {BaseLoader} from "@components/ui/BaseLoader.jsx";
import styles from "@assets/styles/module/Profile.module.css";
import {getCurrentUser} from "@api/user.js";
import {useEffect, useState} from "react";

export function BaseProfileContainer() {
    const [user, setUser] = useState(null);
    useEffect(() => {

        const getData = async () => {
            try {
                let response = await getCurrentUser(window.WebApp.initDataUnsafe.user.id);
                setUser(response.data);
            } catch (error) {
                console.error(error);
            }
        }
        getData();
    }, []);

    return (user ? <BaseProfileView user={user}/> : <BaseLoader style={{minHeight: "600px"}}/>);
}

export function BaseProfileView(props) {
    return (
        <>
            <Panel
                className={styles.page}
            >
                <Flex
                    direction="column"
                    gap={24}
                >
                    <Container className={styles.header}>
                        <Flex
                            direction="column"
                            align="center"
                            gap={16}
                        >
                            <Avatar.Container
                                size={96}
                            >
                                <Avatar.Image
                                    fallback="ME"
                                    src={window.WebApp.initDataUnsafe.user.photo_url}
                                />
                            </Avatar.Container>

                            <Flex
                                className={styles.details}
                                direction="column"
                                align="center"
                            >
                                <Typography.Headline
                                    variant="large-strong">
                                    {
                                        window.WebApp.initDataUnsafe.user?.last_name + " " +
                                        window.WebApp.initDataUnsafe.user?.first_name
                                    }
                                </Typography.Headline>
                                <Typography.Headline variant="medium">
                                    {props.user?.current_status}
                                </Typography.Headline>

                                <div style={{
                                    display: 'flex',
                                    gap: '32px',
                                    marginTop: '16px'
                                }}>
                                    <div style={{
                                        display: 'flex',
                                        flexDirection: 'column',
                                        alignItems: 'center',
                                        gap: '4px'
                                    }}>
                                        <div style={{
                                            fontSize: '20px',
                                            fontWeight: 'bold',
                                            color: '#007AFF'
                                        }}>
                                            {props.user?.sent_reports_count || 0}
                                        </div>
                                        <div style={{
                                            fontSize: '12px',
                                            color: '#8E8E93'
                                        }}>
                                            Заявок
                                        </div>
                                    </div>

                                    <div style={{
                                        display: 'flex',
                                        flexDirection: 'column',
                                        alignItems: 'center',
                                        gap: '4px'
                                    }}>
                                        <div style={{
                                            fontSize: '20px',
                                            fontWeight: 'bold',
                                            color: '#34C759'
                                        }}>
                                            {props.user?.total_points || 0}
                                        </div>
                                        <div style={{
                                            fontSize: '12px',
                                            color: '#8E8E93'
                                        }}>
                                            Очков
                                        </div>
                                    </div>
                                </div>
                            </Flex>
                        </Flex>
                    </Container>
                </Flex>
            </Panel>
        </>
    );
}