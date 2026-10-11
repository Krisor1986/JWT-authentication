import { createBrowserRouter, Navigate } from "react-router-dom";
import { Layout } from "./pages/Layout";
import { Single } from "./pages/Single";
import { Home } from "./pages/Home";
import { Signup } from "./pages/Signup";
import { Login } from "./pages/Login";
import { Private } from "./pages/Private";

export const router = createBrowserRouter([{
    path: "/",
    element: <Layout />,
    children: [
        { index: true, element: <Home /> },
        { path: "details/:category/:uid", element: <Single /> },
        { path: "signup", element: <Signup /> },
        { path: "login", element: <Login /> },
        { path: "private", element: <Private /> },
        { path: "*", element: <Navigate to="/" replace /> }
    ]
}]);
