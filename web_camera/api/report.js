import axios from "axios";

export async function sendReport(data) {
    try {
        return await axios.post(__BASE__PYTHON__URL__ + '/api/reports/draft', data);
    } catch (e) {
        console.error(e);
    }
}