import axios from "axios";

export function downloadMedias(data) {
    return axios.post(__BASE__PYTHON__URL__ + '/api/detect/images', data);
}