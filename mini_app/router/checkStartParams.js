import { redirect } from "react-router";

export const checkStartParam = () => {
    if (window.WebApp.initDataUnsafe.start_param) {
        return redirect(`/send-report/${window.WebApp.initDataUnsafe.start_param}`);
    }
    return null;
};