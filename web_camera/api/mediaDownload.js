import axios from "axios";

export async function downloadMedias(data) {
    try {
       return await axios.post(__BASE__PYTHON__URL__ + '/api/detect/images', data);
    } catch (e) {
        console.error(e);
    }
}