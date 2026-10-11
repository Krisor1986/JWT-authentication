import PropTypes from "prop-types";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import useGlobalReducer from "../hooks/useGlobalReducer";

const cardFields = {
  people: [
    ["height", "Height"],
    ["mass", "Mass"],
    ["gender", "Gender"],
  ],
  planets: [
    ["climate", "Climate"],
    ["terrain", "Terrain"],
    ["population", "Population"],
  ],
  vehicles: [
    ["model", "Model"],
    ["manufacturer", "Manufacturer"],
    ["passengers", "Passengers"],
  ],
};

export const StarWarsCard = ({ item, category, imageUrl }) => {
  const properties = item.properties;
  const [failedImage, setFailedImage] = useState(null);
  const { store, token, toggleFavorite, favoritesLoading, pendingFavorite } = useGlobalReducer();
  const navigate = useNavigate();

  const isFavorite = store.favorites.some(
    (favorite) => favorite.category === category && String(favorite.uid) === String(item.uid),
  );
  return (
    <article className="card h-100 overflow-hidden">
      {imageUrl && failedImage !== imageUrl ? (
        <img
          src={imageUrl}
          alt={properties.name}
          className="card-img-top d-block mx-auto"
          style={{ width: "100%", height: "auto" }}
          loading="lazy"
          onError={() => setFailedImage(imageUrl)}
        />
      ) : (
        <div
          className="bg-secondary text-white d-flex align-items-center justify-content-center"
          style={{ height: "240px" }}
        >
          Image not available
        </div>
      )}
      <div className="card-body d-flex flex-column p-3">
        <h3 className="card-title h5">{properties.name}</h3>

        {cardFields[category].map(([field, label]) => (
          <p className="card-text small mb-1" key={field}>
            <strong>{label}:</strong> {properties[field] || "Not available"}
          </p>
        ))}
        <div className="d-flex justify-content-between mt-auto pt-2">
          <Link
            to={`/details/${category}/${item.uid}`}
            className="btn btn-outline-primary"
          >
            Learn more
          </Link>
          <button
            className={`btn ${
              isFavorite ? "btn-warning" : "btn-outline-warning"
            }`}
            aria-label={
              isFavorite
                ? `Remove ${properties.name} from favorites`
                : `Add ${properties.name} to favorites`
            }
            aria-pressed={isFavorite}
            disabled={favoritesLoading || pendingFavorite}
            onClick={() => {
              if (!token) { navigate("/login"); return; }
              toggleFavorite({
                  category,
                  uid: item.uid,
                  name: properties.name,
              });
            }}
          >
            <span aria-hidden="true">{isFavorite ? "★" : "☆"}</span>
          </button>
        </div>
      </div>
    </article>
  );
};

StarWarsCard.propTypes = {
  item: PropTypes.shape({
    uid: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    properties: PropTypes.shape({ name: PropTypes.string.isRequired }).isRequired,
  }).isRequired,
  category: PropTypes.oneOf(["people", "planets", "vehicles"]).isRequired,
  imageUrl: PropTypes.string,
};
