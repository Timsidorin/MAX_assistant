import { CreatePage } from "../pages/CreatePage";
import { ProfilePage } from "../pages/ProfilePage.jsx";
import { Navigate, createBrowserRouter } from "react-router";
import { Layout } from "../layout/Layout.jsx";

export const router = createBrowserRouter([
    {
        path: "/",
        element: <Navigate to="/create" replace />,
    },
    {
        path: "/",
        element: <Layout />,
        children: [
            {
                path: "create",
                element: <CreatePage/>,
            },
            {
                path: "profile",
                element: <ProfilePage/>,
            }
        ]
    }
]);