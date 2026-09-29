function requestPosition(options) {
    return new Promise(resolve => {
        navigator.geolocation.getCurrentPosition(
            position => resolve({status: true, message: 'Координаты определены', data: position.coords}),
            error => resolve({status: false, error}),
            options
        );
    });
}

export async function getLocation() {
    if (!window.isSecureContext) {
        return {status: false, message: 'Геолокация доступна только через HTTPS', data: null};
    }
    if (!navigator.geolocation) {
        return {status: false, message: 'Геолокация не поддерживается этим браузером', data: null};
    }

    const precise = await requestPosition({
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 30000,
    });
    if (precise.status) {
        return precise;
    }

    if (precise.error?.code !== 1) {
        const approximate = await requestPosition({
            enableHighAccuracy: false,
            timeout: 8000,
            maximumAge: 300000,
        });
        if (approximate.status) {
            return approximate;
        }
    }

    const messages = {
        1: 'MAX или iPhone не предоставил доступ к геопозиции',
        2: 'Не удалось определить местоположение',
        3: 'Определение геопозиции заняло слишком много времени',
    };
    return {
        status: false,
        message: messages[precise.error?.code] || 'Не удалось получить геопозицию',
        data: precise.error,
    };
}
