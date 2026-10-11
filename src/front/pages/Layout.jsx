import { Outlet } from "react-router-dom";
import { Navbar } from "../components/Navbar";
import { Footer } from "../components/Footer";
export const Layout = () => <div className="app-layout"><Navbar /><main className="container py-5"><Outlet /></main><Footer /></div>;
