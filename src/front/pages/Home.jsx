import { useEffect, useState } from "react";
import { StarWarsCard } from "../components/StarWarsCard";
import { toBlogItem } from "../utils/catalog";
import { API_URL } from "../hooks/useGlobalReducer";
import useGlobalReducer from "../hooks/useGlobalReducer";

const categories = [
  { key: "people", title: "Characters" },
  { key: "planets", title: "Planets" },
  { key: "vehicles", title: "Vehicles" },
];

export const Home = () => {
  const { store, dispatch } = useGlobalReducer();
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    const loadCategory = async (category) => {
      try {
        const response = await fetch(
          `${API_URL}/${category}`,
        );

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        dispatch({
          type: `set_${category}`,
          payload: data.map(toBlogItem),
        });
      } catch (error) {
        console.error(error);

        setErrors((previous) => ({
          ...previous,
          [category]: "Could not load this list.",
        }));
      }
    };

    Promise.all(categories.map(({ key }) => loadCategory(key))).finally(() =>
      setLoading(false),
    );
  }, [dispatch]);
  return (
    <main className="container py-4">
      <h1 className="mb-4">Star Wars Blog</h1>

      {categories.map(({ key, title }) => (
        <section className="mb-5" key={key}>
          <h2 className="text-danger mb-3">{title}</h2>

          {errors[key] ? (
            <p className="alert alert-danger" role="alert">
              {errors[key]}
            </p>
          ) : loading ? (
            <p>Loading…</p>
          ) : (
            <div className="row g-3">
              {store[key].map((item) => (
                <div className="col-12 col-md-6 col-lg-4" key={item.uid}>
                  <StarWarsCard
                    item={item}
                    category={key}
                    imageUrl={item.image_url}
                  />
                </div>
              ))}
            </div>
          )}
        </section>
      ))}
    </main>
  );
};
