import {Navigate} from "react-router";
import {Layout} from "../layout/Layout.jsx";
import {CreatePage, ManualCreatePage, ProfilePage, SelectedPositionPage, SendReportPage} from "@pages";
import {checkStartParam} from "./checkStartParams.js";

export const routes = [
    {
        path: "/",
        element: <><Layout /><Navigate to="/create" replace /></>,
        loader: checkStartParam,
        children: [
            {
                path: "create",
                element: <CreatePage/>,
            },
            {
                path: "profile",
                element: <ProfilePage/>,
            },
        ],
    },
    {
        path: "manual-create/:long/:lat",
        element: <ManualCreatePage/>,
    },
    {
        path: "selected-position",
        element: <SelectedPositionPage/>,
    },
    {
        path: "send-report/:uuid",
        element: <SendReportPage/>,
    }
]