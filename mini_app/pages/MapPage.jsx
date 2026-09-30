import mmrgl from 'mmr-gl';
import { useEffect, useRef, useState } from 'react';
import { Button, Flex, Typography } from "@maxhub/max-ui";
import 'mmr-gl/dist/mmr-gl.css';
import { BaseLoader } from "@components/ui/BaseLoader.jsx";
import { getGeoReports, getReportsStats, confirmReport } from "@api/report.js";
import toast from "react-hot-toast";

const PRIORITY_COLORS = {
    critical: '#FF3B30',
    high: '#FF9500',
    medium: '#FFCC00',
    low: '#34C759',
};

const FALLBACK_STYLE = 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json';

function getMapStyle() {
    return import.meta.env.VITE_VK_MAP_API ? 'mmr://api/styles/main_style.json' : FALLBACK_STYLE;
}

const STATUS_LABELS = {
    submitted: 'Отправлена',
    in_review: 'На рассмотрении',
    in_progress: 'В работе',
    completed: 'Выполнена',
};

function timeAgo(dateString) {
    const diff = Date.now() - new Date(dateString).getTime();
    const minutes = Math.floor(diff / 60000);
    if (minutes < 1) return 'только что';
    if (minutes < 60) return `${minutes} мин назад`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} ч назад`;
    return `${Math.floor(hours / 24)} дн назад`;
}

function toGeoJSON(points) {
    return {
        type: 'FeatureCollection',
        features: points.map((p) => ({
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [p.longitude, p.latitude] },
            properties: {
                uuid: p.uuid,
                address: p.address || 'Адрес не указан',
                status: STATUS_LABELS[p.status] || p.status,
                priority: p.priority,
                max_risk: p.max_risk,
                total_potholes: p.total_potholes,
                confirmations: p.confirmations || 0,
            },
        })),
    };
}

export function MapPage() {
    const mapContainer = useRef(null);
    const map = useRef(null);
    const [isMapLoaded, setIsMapLoaded] = useState(false);
    const [mode, setMode] = useState('points');
    const [count, setCount] = useState(0);
    const [stats, setStats] = useState(null);

    useEffect(() => {
        mmrgl.accessToken = import.meta.env.VITE_VK_MAP_API || '';

        map.current = new mmrgl.Map({
            container: mapContainer.current,
            zoom: 10,
            center: [37.6165, 55.7505],
            style: getMapStyle(),
        });

        map.current.on('load', async () => {
            let points = [];
            try {
                const [geoResp, statsResp] = await Promise.all([getGeoReports(), getReportsStats()]);
                points = geoResp?.data || [];
                if (statsResp) setStats(statsResp.data);
            } catch (e) {
                console.error('Ошибка загрузки точек:', e);
            }
            setCount(points.length);

            const geojson = toGeoJSON(points);
            map.current.addSource('reports', {
                type: 'geojson',
                data: geojson,
                cluster: true,
                clusterRadius: 50,
            });

            map.current.addLayer({
                id: 'reports-clusters',
                type: 'circle',
                source: 'reports',
                filter: ['has', 'point_count'],
                paint: {
                    'circle-radius': ['step', ['get', 'point_count'], 18, 5, 24, 20, 32],
                    'circle-color': ['step', ['get', 'point_count'], '#007AFF', 5, '#FF9500', 20, '#FF3B30'],
                    'circle-opacity': 0.85,
                    'circle-stroke-width': 2,
                    'circle-stroke-color': '#ffffff',
                },
            });

            map.current.addLayer({
                id: 'reports-cluster-count',
                type: 'symbol',
                source: 'reports',
                filter: ['has', 'point_count'],
                layout: {
                    'text-field': '{point_count_abbreviated}',
                    'text-size': 13,
                },
                paint: { 'text-color': '#ffffff' },
            });

            map.current.addLayer({
                id: 'reports-points',
                type: 'circle',
                source: 'reports',
                filter: ['!', ['has', 'point_count']],
                paint: {
                    'circle-radius': ['interpolate', ['linear'], ['get', 'max_risk'], 0, 7, 100, 14],
                    'circle-color': [
                        'match', ['get', 'priority'],
                        'critical', PRIORITY_COLORS.critical,
                        'high', PRIORITY_COLORS.high,
                        'medium', PRIORITY_COLORS.medium,
                        PRIORITY_COLORS.low,
                    ],
                    'circle-stroke-width': 2,
                    'circle-stroke-color': '#ffffff',
                },
            });

            map.current.addLayer({
                id: 'reports-heat',
                type: 'heatmap',
                source: 'reports',
                layout: { visibility: 'none' },
                paint: {
                    'heatmap-weight': [
                        'interpolate', ['linear'], ['get', 'max_risk'],
                        0, 0.2,
                        100, 1,
                    ],
                    'heatmap-intensity': 1.2,
                    'heatmap-radius': 30,
                    'heatmap-opacity': 0.8,
                },
            });

            map.current.on('click', 'reports-clusters', async (e) => {
                const clusterId = e.features[0].properties.cluster_id;
                const coords = e.features[0].geometry.coordinates.slice();
                try {
                    const zoom = await map.current.getSource('reports').getClusterExpansionZoom(clusterId);
                    map.current.easeTo({ center: coords, zoom });
                } catch (_) {
                    map.current.easeTo({ center: coords, zoom: map.current.getZoom() + 2 });
                }
            });

            map.current.on('click', 'reports-points', (e) => {
                const props = e.features[0].properties;
                const coords = e.features[0].geometry.coordinates.slice();

                const container = document.createElement('div');
                container.style.maxWidth = '230px';
                container.innerHTML = `
                    <b>${props.address}</b><br/>
                    Статус: ${props.status}<br/>
                    Риск: ${Number(props.max_risk).toFixed(0)}%<br/>
                    Дефектов: ${props.total_potholes}<br/>
                    <span class="confirm-count">👍 Подтверждений: ${props.confirmations}</span>
                `;

                const btn = document.createElement('button');
                btn.textContent = '✋ Я тоже тут видел яму';
                btn.style.cssText = 'margin-top:8px;width:100%;padding:6px;border:none;border-radius:8px;background:#007AFF;color:#fff;font-size:12px;cursor:pointer;';
                btn.onclick = async () => {
                    btn.disabled = true;
                    const resp = await confirmReport(props.uuid);
                    if (resp) {
                        container.querySelector('.confirm-count').textContent = `👍 Подтверждений: ${resp.data.confirmations}`;
                        toast.success('Подтверждено! Приоритет заявки вырос');
                        btn.textContent = '✔ Подтверждено';
                    } else {
                        btn.disabled = false;
                        toast.error('Не удалось подтвердить');
                    }
                };
                container.appendChild(btn);

                new mmrgl.Popup({ closeButton: true })
                    .setLngLat(coords)
                    .setDOMContent(container)
                    .addTo(map.current);
            });

            for (const layerId of ['reports-points', 'reports-clusters']) {
                map.current.on('mouseenter', layerId, () => {
                    map.current.getCanvas().style.cursor = 'pointer';
                });
                map.current.on('mouseleave', layerId, () => {
                    map.current.getCanvas().style.cursor = '';
                });
            }

            map.current.addControl(new mmrgl.NavigationControl({ showCompass: false }), 'top-right');
            map.current.addControl(new mmrgl.FullscreenControl(), 'top-right');

            if (points.length > 0) {
                const newest = points[0];
                const pulseEl = document.createElement('div');
                pulseEl.className = 'pothole-pulse-marker';
                pulseEl.innerHTML = '<div class="pulse-dot"></div><div class="pulse-ring"></div>';
                new mmrgl.Marker({ element: pulseEl })
                    .setLngLat([newest.longitude, newest.latitude])
                    .addTo(map.current);
            }

            if (points.length > 0) {
                const avgLng = points.reduce((s, p) => s + p.longitude, 0) / points.length;
                const avgLat = points.reduce((s, p) => s + p.latitude, 0) / points.length;
                map.current.flyTo({ center: [avgLng, avgLat], zoom: 11 });
            }

            setIsMapLoaded(true);
        });

        return () => {
            if (map.current) {
                map.current.remove();
                map.current = null;
            }
        };
    }, []);

    const toggleMode = (next) => {
        setMode(next);
        if (!map.current) return;
        const pointsVis = next === 'points' ? 'visible' : 'none';
        map.current.setLayoutProperty('reports-points', 'visibility', pointsVis);
        map.current.setLayoutProperty('reports-clusters', 'visibility', pointsVis);
        map.current.setLayoutProperty('reports-cluster-count', 'visibility', pointsVis);
        map.current.setLayoutProperty('reports-heat', 'visibility', next === 'heat' ? 'visible' : 'none');
    };

    return (
        <div style={{ padding: '10px', paddingBottom: '80px' }}>
            <style>{`
                .pothole-pulse-marker { position: relative; width: 20px; height: 20px; }
                .pulse-dot {
                    position: absolute; inset: 5px; border-radius: 50%;
                    background: #FF3B30; border: 2px solid #fff; z-index: 2;
                }
                .pulse-ring {
                    position: absolute; inset: 0; border-radius: 50%;
                    background: rgba(255,59,48,0.4);
                    animation: pothole-pulse 1.6s ease-out infinite;
                }
                @keyframes pothole-pulse {
                    0% { transform: scale(0.6); opacity: 1; }
                    100% { transform: scale(3); opacity: 0; }
                }
            `}</style>
            <Flex direction="row" justify="between" align="center" style={{ marginBottom: '10px' }}>
                <Typography.Title>Карта дефектов</Typography.Title>
                <Flex direction="row" gap={4}>
                    <Button size="small" mode={mode === 'points' ? 'primary' : 'secondary'} onClick={() => toggleMode('points')}>
                        Точки
                    </Button>
                    <Button size="small" mode={mode === 'heat' ? 'primary' : 'secondary'} onClick={() => toggleMode('heat')}>
                        Теплокарта
                    </Button>
                </Flex>
            </Flex>
            {stats && (
                <div style={{
                    display: 'flex',
                    gap: '12px',
                    overflowX: 'auto',
                    padding: '8px 12px',
                    marginBottom: '8px',
                    borderRadius: '12px',
                    background: 'linear-gradient(90deg, rgba(0,122,255,0.08), rgba(255,59,48,0.08))',
                    fontSize: '12px',
                    whiteSpace: 'nowrap',
                }}>
                    <span>🕳 Дефектов: <b>{stats.total_reports}</b></span>
                    <span>🔴 Критических: <b>{stats.critical_count}</b></span>
                    <span>📸 Ям найдено: <b>{stats.total_potholes}</b></span>
                    {stats.worst_address && (
                        <span>⚠️ Опаснее всего: <b>{stats.worst_address}</b> ({stats.worst_risk.toFixed(0)}%)</span>
                    )}
                    {stats.last_report_at && (
                        <span>🕒 Последняя: <b>{timeAgo(stats.last_report_at)}</b></span>
                    )}
                </div>
            )}
            <Typography.Body style={{ marginBottom: '8px', color: '#8E8E93' }}>
                Заявок на карте: {count}
            </Typography.Body>

            {!isMapLoaded && (
                <div style={{ width: '100%', height: '70vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                    <BaseLoader />
                </div>
            )}

            <div
                ref={mapContainer}
                style={{
                    width: '100%',
                    height: '70vh',
                    borderRadius: '12px',
                    display: isMapLoaded ? 'block' : 'none',
                }}
            />
        </div>
    );
}
