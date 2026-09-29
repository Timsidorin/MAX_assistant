import axios from "axios";

export async function getCurrentUser(id) {
    try {
        return await axios.get(__BASE__PYTHON__URL__ + `/api/users/${id}`);
    } catch (error) {
        console.error(error);
    }
}

export async function getLeaderboard(limit = 5) {
    try {
        return await axios.get(__BASE__PYTHON__URL__ + `/api/users/leaderboard`, {
            params: { limit }
        });
    } catch (error) {
        console.error(error);
    }
}

export async function getUserRank(id) {
    try {
        return await axios.get(__BASE__PYTHON__URL__ + `/api/users/${id}/rank`);
    } catch (error) {
        console.error(error);
    }
}