import axios from "axios";

export function sendReport(data) {
    return axios.post(__BASE__PYTHON__URL__ + '/api/reports/draft', data);
}