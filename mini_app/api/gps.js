import axios from 'axios';

export function searchAdress(params) {
    try {
        return axios.get(`https://maps.vk.com/api/search`,
            {
                params:
                    {
                        api_key: import.meta.env.VITE_VK_MAP_API,
                        ...params
                    }
            });
    } catch (error) {
        console.error(error);
    }
}