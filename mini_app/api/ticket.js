import axios from "axios";

export async function getTicket(params = {}) {
    try {
        return await axios.get(__BASE__PYTHON__URL__ + "/api/reports", {
            params: params
        });
    } catch (error) {
        console.error(error);
    }
}

export async function postTicket(uuid) {
    try {
        return await axios.post(__BASE__PYTHON__URL__ + `/api/reports/submit/${uuid}`);
    } catch (error) {
        console.error(error);
    }
}