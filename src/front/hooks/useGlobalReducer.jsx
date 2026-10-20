import { createContext, useCallback, useContext, useEffect, useMemo, useReducer, useState } from "react";
import PropTypes from "prop-types";
import storeReducer, { initialStore } from "../store";

const StoreContext = createContext(null);
const backendUrl = (import.meta.env.VITE_BACKEND_URL || "").trim().replace(/\/+$/, "");
export const API_URL = backendUrl.endsWith("/api") ? backendUrl : `${backendUrl}/api`;
const flattenFavorites = data => Object.entries(data).flatMap(([category, records]) => records.map(record => ({ category, uid: String(record.id), name: record.name })));

export function StoreProvider({ children }) {
    const [store, rawDispatch] = useReducer(storeReducer, undefined, initialStore);
    const [token, setToken] = useState(() => sessionStorage.getItem("token"));
    const [favoriteError, setFavoriteError] = useState("");
    const [favoritesLoading, setFavoritesLoading] = useState(false);
    const [pendingFavorite, setPendingFavorite] = useState(false);
    const login = useCallback(value => {
        sessionStorage.setItem("token", value);
        rawDispatch({ type: "set_favorites", payload: [] });
        setFavoriteError("");
        setToken(value);
    }, []);
    const logout = useCallback(() => {
        sessionStorage.removeItem("token");
        rawDispatch({ type: "set_favorites", payload: [] });
        setFavoriteError("");
        setFavoritesLoading(false);
        setToken(null);
    }, []);
    useEffect(() => {
        if (!token) return;
        const controller = new AbortController();
        setFavoritesLoading(true);
        async function loadFavorites() {
            try {
                const response = await fetch(`${API_URL}/users/favorites`, { headers: { Authorization: `Bearer ${token}` }, signal: controller.signal });
                if (response.status === 401) { logout(); return; }
                const data = await response.json();
                if (!response.ok) throw new Error(data.message);
                rawDispatch({ type: "set_favorites", payload: flattenFavorites(data) });
            } catch (problem) {
                if (problem.name !== "AbortError") setFavoriteError("Could not load your favorites. Reload to try again.");
            } finally {
                if (!controller.signal.aborted) setFavoritesLoading(false);
            }
        }
        loadFavorites();
        return () => controller.abort();
    }, [token, logout]);
    const toggleFavorite = useCallback(async item => {
        if (!token || pendingFavorite || favoritesLoading || favoriteError) return;
        setPendingFavorite(true);
        const exists = store.favorites.some(favorite => favorite.category === item.category && favorite.uid === String(item.uid));
        try {
            const response = await fetch(`${API_URL}/favorite/${item.category}/${item.uid}`, {
                method: exists ? "DELETE" : "POST", headers: { Authorization: `Bearer ${token}` }
            });
            if (response.status === 401) { logout(); return; }
            const data = await response.json();
            if (!response.ok) throw new Error(data.message);
            if (sessionStorage.getItem("token") === token) rawDispatch({ type: "toggle_favorite", payload: item });
        } catch (problem) {
            setFavoriteError(problem.message || "Could not save favorite.");
        } finally { setPendingFavorite(false); }
    }, [token, pendingFavorite, favoritesLoading, favoriteError, store.favorites, logout]);
    const value = useMemo(() => ({ token, login, logout, store, dispatch: rawDispatch, toggleFavorite, favoriteError, favoritesLoading, pendingFavorite }), [token, login, logout, store, toggleFavorite, favoriteError, favoritesLoading, pendingFavorite]);
    return <StoreContext.Provider value={value}>{children}</StoreContext.Provider>;
}
StoreProvider.propTypes = { children: PropTypes.node.isRequired };
export default function useGlobalReducer() { return useContext(StoreContext); }
