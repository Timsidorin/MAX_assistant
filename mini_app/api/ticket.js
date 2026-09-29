import axios from "axios";

export async function getTicket(params = {}) {
    try {
        return await axios.get(__BASE__PYTHON__URL__ + "/api/reports/", {
            params: params
        });
    } catch (error) {
        console.error(error);
    }
}

export function postTicket(uuid) {
    return axios.post(__BASE__PYTHON__URL__ + `/api/reports/submit/${uuid}`);
}

export async function sendReport(data) {
    try {
        return await axios.post(__BASE__PYTHON__URL__ + '/api/reports/draft', data);
    } catch (e) {
        console.error(e);
    }
}