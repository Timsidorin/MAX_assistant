import React, { useEffect, useState } from 'react';
import styles from '../../../assets/styles/module/TickedCard.module.css';
import {Typography} from "@maxhub/max-ui";
import {getTicket} from "@api/ticket.js";

function TickedCardView({ ticket }) {
  const statusClass = ticket.status.toLowerCase() === 'в процессе' 
    ? styles.statusActive 
    : styles.statusCompleted;

  return (
    <div className={styles.card}>
      <Typography.Title>{ticket.address}</Typography.Title>
      <div>{ticket.description}</div>
      <div>Дата: <strong>{new Date(ticket.date).toLocaleDateString('ru-RU')}</strong></div>
      <div>Статус: <span className={`${styles.status} ${statusClass}`}>
        {ticket.status}
      </span></div>
    </div>
  );
}

export function TickedCardContainer() {
    const [tickets, setTickets] = useState([]);

    useEffect(() => {
        const fetchTicket = async () => {
            try {
                const response = await getTicket({
                    user_id: window.WebApp.initDataUnsafe.user.id,
                    skip: 0,
                    limit: 50,
                });
                setTickets(Array.isArray(response) ? response : []);
            } catch (error) {
                console.error('Ошибка загрузки тикетов:', error);
                setTickets([]);
            }
        };
        fetchTicket();
    }, []);

    if (tickets.length === 0) {
        return <div>Нет данных</div>;
    }

    return (
        <>
            {tickets.map((ticket) => (
                <TickedCardView key={ticket.id} ticket={ticket} />
            ))}
        </>
    );
}