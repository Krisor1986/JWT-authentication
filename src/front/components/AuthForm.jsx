import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import PropTypes from "prop-types";
import useGlobalReducer, { API_URL } from "../hooks/useGlobalReducer";

export function AuthForm({ signup = false }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);
    const { login } = useGlobalReducer();
    const navigate = useNavigate();
    const location = useLocation();

    async function handleSubmit(event) {
        event.preventDefault();
        setError("");
        setBusy(true);
        try {
            const response = await fetch(`${API_URL}/${signup ? "signup" : "login"}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.message || "Unable to complete your request.");
            if (signup) {
                navigate("/login", { replace: true, state: { message: data.message } });
            } else {
                login(data.token);
                navigate("/private", { replace: true });
            }
        } catch (problem) {
            setError(problem instanceof TypeError ? "Cannot connect to the backend. Please try again." : problem.message);
        } finally {
            setBusy(false);
        }
    }

    return <section className="card auth-card shadow-sm mx-auto">
        <div className="card-body p-4 p-md-5">
            <h1 className="h3 mb-2">{signup ? "Create your account" : "Welcome back"}</h1>
            <p className="text-secondary mb-4">{signup ? "Sign up with your email and password." : "Log in to access your private page."}</p>
            {location.state?.message && <div className="alert alert-success" role="status">{location.state.message}</div>}
            {error && <div className="alert alert-danger" role="alert">{error}</div>}
            <form onSubmit={handleSubmit}>
                <label className="form-label" htmlFor="email">Email</label>
                <input id="email" className="form-control mb-3" type="email" autoComplete="email" maxLength={120} required value={email} onChange={event => setEmail(event.target.value)} />
                <label className="form-label" htmlFor="password">Password</label>
                <input id="password" className="form-control" type="password" autoComplete={signup ? "new-password" : "current-password"} minLength={signup ? 8 : 1} maxLength={128} required value={password} onChange={event => setPassword(event.target.value)} />
                {signup && <p className="form-text">Use between 8 and 128 characters.</p>}
                <button className="btn btn-primary w-100 mt-4" disabled={busy} type="submit">{busy ? "Please wait…" : signup ? "Sign up" : "Log in"}</button>
            </form>
            <p className="text-center mt-4 mb-0">{signup ? "Already have an account? " : "New here? "}<Link to={signup ? "/login" : "/signup"}>{signup ? "Log in" : "Sign up"}</Link></p>
        </div>
    </section>;
}
AuthForm.propTypes = { signup: PropTypes.bool };
