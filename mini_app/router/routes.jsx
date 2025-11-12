import {Navigate} from "react-router";
import {Layout} from "../layout/Layout.jsx";
import {CreatePage} from "../pages/CreatePage.jsx";
import {ProfilePage} from "../pages/ProfilePage.jsx";
import {ManualCreatePage} from "../pages/ManualCreatePage.jsx";
import {SelectedPositionPage} from "../pages/SelectedPositionPage.jsx";

export const routes = [
    {
        path: "/",
        element: <><Layout /><Navigate to="/create" replace /></>,
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
        path: "manual-create",
        element: <ManualCreatePage/>,
    },
    {
        path: "selected-position",
        element: <SelectedPositionPage/>,
    }
]