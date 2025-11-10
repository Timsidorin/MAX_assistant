import { BottomToolBar } from "./BottomToolBar.jsx";
import { Outlet } from "react-router";

export function Layout() {
    return (
        <>
            <div>
                <Outlet />
            </div>
            <BottomToolBar/>
        </>
    );
}