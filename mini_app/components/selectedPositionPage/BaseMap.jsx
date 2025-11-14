import mmrgl from 'mmr-gl';
import {useEffect, useRef, useCallback, useState} from 'react';
import {Button, Flex} from "@maxhub/max-ui";
import 'mmr-gl/dist/mmr-gl.css';
import {InputAdressSearch} from "@components/selectedPositionPage/InputAdressSearch.jsx"
import {useNavigate} from "react-router";
import {BaseLoader} from "@components/ui/BaseLoader.jsx";

export function BaseMap() {
    const mapContainer = useRef(null);
    const map = useRef(null);
    const marker = useRef(null);
    const navigate = useNavigate();
    const [selectedPosition, setSelectedPosition] = useState([37.6165, 55.7505]);
    const [isMapLoaded, setIsMapLoaded] = useState(false);

    useEffect(() => {
        mmrgl.accessToken = import.meta.env.VITE_VK_MAP_API;

        map.current = new mmrgl.Map({
            container: 'map',
            zoom: 8,
            center: selectedPosition,
            style: 'mmr://api/styles/main_style.json',
            hash: true,
        });

        // Создаем маркер после загрузки карты
        map.current.on('load', () => {
            createMarker();
            setIsMapLoaded(true);
        });

        return () => {
            if (map.current) {
                map.current.remove();
                map.current = null;
            }
        };
    }, []);

    // Функция для обновления позиции
    const updatePosition = useCallback((newPosition) => {
        setSelectedPosition(newPosition);

        // Перемещаем центр карты
        if (map.current) {
            map.current.flyTo({
                center: newPosition,
                essential: true
            });
        }

        // Обновляем позицию маркера
        if (marker.current) {
            marker.current.setLngLat(newPosition);
        } else {
            // Если маркера нет, создаем его
            createMarker(newPosition);
        }
    }, []);

    const createMarker = useCallback((position = selectedPosition) => {
        if (marker.current) {
            marker.current.remove();
        }

        marker.current = new mmrgl.Marker({
            color: "#ff0b0b",
            draggable: true
        })
            .setLngLat(position)
            .addTo(map.current);

        marker.current.on('dragend', () => {
            const lngLat = marker.current.getLngLat();
            const newPosition = [lngLat.lng, lngLat.lat];
            setSelectedPosition(newPosition);
        });
    }, [selectedPosition]);

    // Обработчик выбора адреса
    const handleAddressSelect = useCallback((address) => {
        if (address.pin) {
            const newPosition = [address.pin[0], address.pin[1]];
            updatePosition(newPosition);
        }
    }, [updatePosition]);

    return (
        <>
            <InputAdressSearch onSelect={handleAddressSelect}/>

            {!isMapLoaded && (
                <div style={{width: '100%', height: '500px', display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                    <BaseLoader />
                </div>
            )}

            <div
                id="map"
                ref={mapContainer}
                style={{
                    width: '100%',
                    height: '500px',
                    marginBottom: '10px',
                    display: isMapLoaded ? 'block' : 'none'
                }}
            />

            <Flex gap={3} style={{marginTop: '10px'}}>
                <Button
                    stretched
                    onClick={() => navigate(`/`)}>
                    Назад
                </Button>
                <Button
                    stretched
                    onClick={
                        () => navigate(`/manual-create/${selectedPosition[0]}/${selectedPosition[1]}`)
                    }>
                    Далее
                </Button>
            </Flex>
        </>
    );
}