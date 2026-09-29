import {RouterProvider} from "react-router/dom";
import {Toaster} from "react-hot-toast";
import {router} from "./router/index.jsx";

export function App() {
    return (
        <>
            <RouterProvider router={router}/>
            <Toaster position="top-center"/>
        </>
    );
}