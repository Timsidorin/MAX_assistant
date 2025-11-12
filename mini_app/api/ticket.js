import axios from "axios";

export async function getTicket(params = {}) {
    try {
        return await axios.get(__BASE__PYTHON__URL__ + "/api/tickets", {
            params: params
        });
    } catch (error) {
        console.error(error);
    }
}