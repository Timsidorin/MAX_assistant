import axios from "axios";

export async function downloadMedias(data) {
    try {
        let response = await axios.post(__BASE__PYTHON__URL__ + '/api/detect/images', data);
        console.log(response.data);
    } catch (e) {
        console.error(e);
    }
}