import { Link, useNavigate } from "react-router-dom";
import useGlobalReducer from "../hooks/useGlobalReducer";
export const Navbar = () => {
    const { token, logout, store, favoriteError } = useGlobalReducer();
    const navigate = useNavigate();
    return <><nav className="navbar bg-light py-3" data-bs-theme="light"><div className="container gap-3">
        <Link className="navbar-brand fw-bold" to="/">STAR WARS</Link>
        <div className="d-flex gap-2 flex-wrap">
            {token ? <><Link className="btn btn-warning" to="/private">Favorites <span className="badge bg-dark ms-1">{store.favorites.length}</span></Link><button className="btn btn-outline-dark" onClick={() => { logout(); navigate("/login", { replace: true }); }}>Log out</button></> : <><Link className="btn btn-outline-dark" to="/login">Log in</Link><Link className="btn btn-warning" to="/signup">Sign up</Link></>}
        </div>
    </div></nav>{favoriteError && <div className="container mt-3"><p className="alert alert-danger" role="alert">{favoriteError}</p></div>}</>;
};
