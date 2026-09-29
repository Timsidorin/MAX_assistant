import axios from "axios";

export async function getGeoReports() {
    try {
        return await axios.get(__BASE__PYTHON__URL__ + "/api/reports/geo");
    } catch (error) {
        console.error(error);
    }
}

export async function getReportsStats() {
    try {
        return await axios.get(__BASE__PYTHON__URL__ + "/api/reports/stats");
    } catch (error) {
        console.error(error);
    }
}

export async function confirmReport(uuid) {
    try {
        return await axios.post(__BASE__PYTHON__URL__ + `/api/reports/${uuid}/confirm`);
    } catch (error) {
        console.error(error);
    }
}
