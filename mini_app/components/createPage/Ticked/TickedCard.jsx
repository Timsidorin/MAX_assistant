import React, {useEffect, useState} from 'react';
import styles from '../../../assets/styles/module/TickedCard.module.css';
import {Typography} from "@maxhub/max-ui";
import {confirmExternalSubmission, getTicket} from "@api/ticket.js";
import {Button} from "@maxhub/max-ui";
import {useNavigate} from "react-router";
import {BaseLoader} from "@components/ui/BaseLoader.jsx";

const StatusIcon = ({ status }) => (
    <div className={`${styles.statusIcon} ${styles[status]}`}>
        {status === 'draft' ? '📝' : '✅'}
    </div>
);

const PriorityBadge = ({ priority }) => {
    const priorityConfig = {
        low: { label: 'Низкий', className: styles.low },
        medium: { label: 'Средний', className: styles.medium },
        high: { label: 'Высокий', className: styles.high }
    };

    const config = priorityConfig[priority] || priorityConfig.medium;

    return (
        <span className={`${styles.priorityBadge} ${config.className}`}>
      {config.label}
    </span>
    );
};

const RiskMeter = ({ risk }) => {
    const riskPercentage = Math.min(100, Math.max(0, risk));
    let riskLevel = 'low';
    if (riskPercentage > 60) riskLevel = 'high';
    else if (riskPercentage > 30) riskLevel = 'medium';

    return (
        <div className={styles.riskMeter}>
            <div className={styles.riskLabel}>
                <span>Уровень риска</span>
                <span className={styles.riskValue}>{riskPercentage.toFixed(1)}%</span>
            </div>
            <div className={styles.riskBar}>
                <div
                    className={`${styles.riskFill} ${styles[riskLevel]}`}
                    style={{ width: `${riskPercentage}%` }}
                />
            </div>
        </div>
    );
};

function TickedCardView({ticket, navigate, onSubmitted}) {
    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('ru-RU', {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        });
    };

    const confirmSubmission = async () => {
        const registrationNumber = window.prompt('Введите регистрационный номер обращения, если он есть') || null;
        await confirmExternalSubmission(ticket.uuid, {
            user_id: window.WebApp?.initDataUnsafe?.user?.id,
            registration_number: registrationNumber,
        });
        onSubmitted(ticket.uuid);
    };

    return (
        <div className={styles.card}>
            <div className={styles.cardHeader}>
                <StatusIcon status={ticket.status} />
                <div className={styles.headerInfo}>
                    <Typography.Title className={styles.address}>
                        {ticket.address}
                    </Typography.Title>
                    <div className={styles.metaInfo}>
            <span className={styles.date}>
              Создан: {formatDate(ticket.created_at)}
            </span>
                        <PriorityBadge priority={ticket.priority} />
                    </div>
                </div>
            </div>

            <div className={styles.cardContent}>
                <div className={styles.stats}>
                    <div className={styles.statItem}>
                        <span className={styles.statLabel}>Ямы обнаружены</span>
                        <span className={styles.statValue}>{ticket.total_potholes}</span>
                    </div>
                    <div className={styles.statItem}>
                        <span className={styles.statLabel}>Макс. риск</span>
                        <span className={styles.statValue}>{ticket.max_risk.toFixed(1)}%</span>
                    </div>
                </div>

                <RiskMeter risk={ticket.max_risk} />

                {ticket.image_urls?.urls?.length > 0 && (
                    <div className={styles.imagesPreview}>
                        <div className={styles.imagesLabel}>
                            📷 Фотографии ({ticket.image_urls.urls.length})
                        </div>
                    </div>
                )}
            </div>

            <div className={styles.cardFooter}>
                {ticket.status === 'draft' ? (
                    <Button
                        onClick={() => navigate(`/send-report/${ticket.uuid}`)}
                        size='small'
                        mode='primary'
                        className={styles.actionButton}
                    >
                        📋 Сформировать отчет
                    </Button>
                ) : ticket.ai_agent_status === 'awaiting_user_submission' ? (
                    <div className={styles.submittedInfo}>
                        <span className={styles.submittedBadge}>Требуется подача через приёмную</span>
                        {ticket.organization_name && <span>{ticket.organization_name}</span>}
                        {ticket.document_url && (
                            <Button size='small' mode='secondary' onClick={() => window.open(ticket.document_url, '_blank')}>
                                Скачать заявление
                            </Button>
                        )}
                        {ticket.organization_website && (
                            <Button size='small' mode='secondary' onClick={() => window.open(ticket.organization_website, '_blank')}>
                                Открыть приёмную
                            </Button>
                        )}
                        <Button size='small' mode='primary' onClick={confirmSubmission}>
                            Я отправил
                        </Button>
                    </div>
                ) : (
                    <div className={styles.submittedInfo}>
                        <span className={styles.submittedBadge}>
                            {ticket.ai_agent_status === 'user_submitted' ? 'Отправка подтверждена' : 'Отчет отправлен'}
                        </span>
                        {ticket.submitted_at && (
                            <span className={styles.submittedDate}>{formatDate(ticket.submitted_at)}</span>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

export function TickedCardContainer() {
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchTicket = async () => {
            try {
                setLoading(true);
                const response = await getTicket({
                    user_id: window.WebApp.initDataUnsafe.user.id,
                    skip: 0,
                    limit: 5,
                });
                setTickets(response.data.items);
            } catch (error) {
                console.error('Ошибка загрузки тикетов:', error);
                setTickets([]);
            } finally {
                setLoading(false);
            }
        };
        fetchTicket();
    }, []);

    const markSubmitted = (uuid) => {
        setTickets((current) => current.map((ticket) => (
            ticket.uuid === uuid ? {...ticket, ai_agent_status: 'user_submitted'} : ticket
        )));
    };

    if (loading) {
        return <BaseLoader style={{ width: '100%' }} />;
    }

    return (
        <div className={styles.cardsContainer}>
            {tickets && tickets.length > 0 ? (
                tickets.map((ticket) => (
                    <TickedCardView
                        navigate={navigate}
                        onSubmitted={markSubmitted}
                        key={ticket.uuid}
                        ticket={ticket}
                    />
                ))
            ) : (
                <div className={styles.emptyState}>
                    <div className={styles.emptyIcon}>📋</div>
                    <Typography.Body className={styles.emptyText}>
                        Нет созданных отчетов
                    </Typography.Body>
                </div>
            )}
        </div>
    );
}