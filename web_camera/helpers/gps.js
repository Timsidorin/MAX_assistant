export function getLocation() {
    return new Promise((resolve, reject) => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                position => {
                    resolve({status: true, message: 'Геолокация поддерживается', data: position.coords});
                },
                error => {
                    reject({status: false, message: 'Ошибка получения геолокации', data: error});
                }
            );
        } else {
            resolve({status: false, message: "Геолокация не поддерживается", data: null});
        }
    });
}