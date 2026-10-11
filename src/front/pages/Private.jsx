import { useEffect, useState } from "react";
import { Link, Navigate } from "react-router-dom";
import useGlobalReducer, { API_URL } from "../hooks/useGlobalReducer";

export const Private = () => {
    const { token, logout, store, toggleFavorite, favoritesLoading, pendingFavorite } = useGlobalReducer();
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");
    const [attempt, setAttempt] = useState(0);

    useEffect(() => {
        if (!token) return;
        const controller = new AbortController();
        let running = false;
        async function validate() {
            if (running) return;
            running = true;
            try {
                const response = await fetch(`${API_URL}/private`, {
                    headers: { Authorization: `Bearer ${token}` },
                    signal: controller.signal
                });
                if (response.status === 401 || response.status === 422) {
                    logout();
                    return;
                }
                const data = await response.json();
                if (!response.ok) throw new Error(data.message || "Unable to validate your session.");
                if (!controller.signal.aborted) {
                    setResult({ token, data });
                    setError("");
                }
            } catch (problem) {
                if (problem.name !== "AbortError") {
                    setResult(null);
                    setError("Cannot validate your session. Check that the backend is running.");
                }
            } finally {
                running = false;
            }
        }
        validate();
        const interval = setInterval(validate, 30000);
        window.addEventListener("focus", validate);
        return () => {
            controller.abort();
            clearInterval(interval);
            window.removeEventListener("focus", validate);
        };
    }, [token, logout, attempt]);

    if (!token) return <Navigate to="/login" replace />;
    if (error) return <div className="alert alert-danger mx-auto auth-card" role="alert">{error}<button className="btn btn-outline-danger d-block mt-3" onClick={() => { setError(""); setAttempt(value => value + 1); }}>Try again</button></div>;
    if (!result || result.token !== token) return <p className="text-center" role="status">Validating your session…</p>;
    return <section className="card auth-card mx-auto shadow-sm"><div className="card-body p-4 p-md-5">
        <span className="badge text-bg-success mb-3">Authenticated</span>
        <h1 className="h3">My favorites</h1>
        <p>{result.data.message}</p>
        <p className="text-secondary mb-0">Signed in as <strong>{result.data.user.email}</strong></p>
        <hr />
        {favoritesLoading ? <p>Loading favorites…</p> : store.favorites.length === 0 ? <p>No favorites yet. <Link to="/">Explore the catalog</Link>.</p> : <ul className="list-group list-group-flush mt-3">{store.favorites.map(item => <li className="list-group-item bg-transparent d-flex justify-content-between gap-3" key={`${item.category}-${item.uid}`}><Link to={`/details/${item.category}/${item.uid}`}>{item.name}</Link><button className="btn btn-sm btn-outline-warning" disabled={pendingFavorite} aria-label={`Remove ${item.name} from favorites`} onClick={() => toggleFavorite(item)}>★</button></li>)}</ul>}
    </div></section>;
};
