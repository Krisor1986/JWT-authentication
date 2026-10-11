import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { EntityDetails } from "../components/EntityDetails";
import { API_URL } from "../hooks/useGlobalReducer";
import { toBlogItem } from "../utils/catalog";

export const Single = () => {
    const { category, uid } = useParams();
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");
    useEffect(() => {
        const controller = new AbortController();
        setResult(null);
        setError("");
        async function load() {
            try {
                const response = await fetch(`${API_URL}/${category}/${uid}`, { signal: controller.signal });
                const data = await response.json();
                if (!response.ok) throw new Error(data.message || "Could not load details.");
                setResult({ key: `${category}/${uid}`, item: toBlogItem(data) });
            } catch (problem) {
                if (problem.name !== "AbortError") setError(problem.message);
            }
        }
        load();
        return () => controller.abort();
    }, [category, uid]);
    if (error) return <p className="alert alert-danger" role="alert">{error}</p>;
    if (!result || result.key !== `${category}/${uid}`) return <p>Loading details…</p>;
    const properties = Object.fromEntries(Object.entries(result.item.properties).map(([field, value]) => [field, Array.isArray(value) ? value.join(", ") || "No records" : value]));
    return <section><Link className="btn btn-outline-light mb-4" to="/">Back home</Link><EntityDetails item={result.item} category={category} properties={properties} imageUrl={result.item.image_url} /></section>;
};
