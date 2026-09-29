import { Flex, Typography } from "@maxhub/max-ui";
import { useEffect, useState } from "react";
import { getLeaderboard } from "@api/user.js";

const MEDALS = ['🥇', '🥈', '🥉'];

export function Leaderboard() {
    const [items, setItems] = useState([]);
    const currentUserId = window.WebApp?.initDataUnsafe?.user?.id;

    useEffect(() => {
        const load = async () => {
            const response = await getLeaderboard(5);
            if (response) setItems(response.data.items);
        };
        load();
    }, []);

    if (!items.length) return null;

    return (
        <div style={{ marginTop: '24px', width: '100%' }}>
            <Flex justify='center' style={{ marginBottom: '12px' }}>
                <Typography.Title>🏆 Топ ямоборцев</Typography.Title>
            </Flex>
            <Flex direction="column" gap={8} style={{ width: '100%' }}>
                {items.map((item) => {
                    const isMe = item.max_user_id === currentUserId;
                    return (
                        <Flex
                            key={item.max_user_id}
                            direction="row"
                            align="center"
                            gap={10}
                            style={{
                                width: '100%',
                                boxSizing: 'border-box',
                                padding: '10px 14px',
                                borderRadius: '12px',
                                backgroundColor: isMe ? 'rgba(0,122,255,0.12)' : 'rgba(142,142,147,0.08)',
                                border: isMe ? '1px solid #007AFF' : '1px solid transparent',
                            }}
                        >
                            <div style={{ width: '28px', fontSize: '16px', fontWeight: 'bold' }}>
                                {MEDALS[item.rank - 1] || `${item.rank}.`}
                            </div>
                            <div style={{ flex: 1 }}>
                                <Typography.Action>
                                    {item.first_name} {item.last_name}
                                </Typography.Action>
                                <div style={{ fontSize: '12px', color: '#8E8E93' }}>
                                    {item.current_status || `Уровень ${item.user_level}`}
                                </div>
                            </div>
                            <div style={{ fontWeight: 'bold', color: '#34C759' }}>
                                {item.total_points}
                            </div>
                        </Flex>
                    );
                })}
            </Flex>
        </div>
    );
}
