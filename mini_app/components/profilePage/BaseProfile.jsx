import {
    Container,
    Flex,
    Avatar,
    Typography,
    Panel,
} from "@maxhub/max-ui";
import {BaseLoader} from "@components/ui/BaseLoader.jsx";
import {Leaderboard} from "@components/profilePage/Leaderboard.jsx";
import {LastedTickedContainer} from "@components/createPage/Ticked/LastedTicked.jsx";
import styles from "@assets/styles/module/Profile.module.css";
import {getCurrentUser, getUserRank} from "@api/user.js";
import {useEffect, useState} from "react";

export function BaseProfileContainer() {
    const [user, setUser] = useState(null);
    const [rank, setRank] = useState(null);
    useEffect(() => {

        const getData = async () => {
            try {
                const userId = window.WebApp?.initDataUnsafe?.user?.id;
                if (!userId) {
                    console.error('window.WebApp.initDataUnsafe.user is not available');
                    setUser(null);
                    return;
                }
                let response = await getCurrentUser(userId);
                if (response) setUser(response.data);
                const rankResponse = await getUserRank(userId);
                if (rankResponse) setRank(rankResponse.data);
            } catch (error) {
                console.error(error);
            }
        }
        getData();
    }, []);

    return (user ? <BaseProfileView user={user} rank={rank}/> : <BaseLoader style={{minHeight: "600px"}}/>);
}

function LevelProgress({rank}) {
    if (!rank) return null;

    const isMax = !rank.next_level_points;
    const progress = isMax ? 100 : Math.min(100, Math.round((rank.total_points / rank.next_level_points) * 100));

    return (
        <div style={{ width: '100%', marginTop: '16px' }}>
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '12px',
                color: '#8E8E93',
                marginBottom: '6px'
            }}>
                <span>Уровень {rank.user_level} · #{rank.rank} в рейтинге</span>
                <span>
                    {isMax
                        ? 'Максимальный уровень'
                        : `${rank.total_points} / ${rank.next_level_points}`}
                </span>
            </div>
            <div style={{
                width: '100%',
                height: '8px',
                borderRadius: '4px',
                backgroundColor: 'rgba(142,142,147,0.2)',
                overflow: 'hidden'
            }}>
                <div style={{
                    width: `${progress}%`,
                    height: '100%',
                    borderRadius: '4px',
                    background: 'linear-gradient(90deg, #007AFF, #34C759)',
                    transition: 'width 0.6s ease'
                }}/>
            </div>
            {!isMax && rank.next_level_name && (
                <div style={{ fontSize: '12px', color: '#8E8E93', marginTop: '6px', textAlign: 'center' }}>
                    До «{rank.next_level_name}» осталось {rank.points_to_next_level} очков
                </div>
            )}
        </div>
    );
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
                            <LevelProgress rank={props.rank}/>
                        </Flex>
                    </Container>
                </Flex>
            </Panel>
            <Leaderboard/>
            <LastedTickedContainer/>
        </>
    );
}