import axios from "axios";

export async function getCurrentUser(id) {
    try {
        return await axios.get(__BASE__PYTHON__URL__ + `/api/users/${id}`);
    } catch (error) {
        console.error(error);
    }
}