import { useNavigate } from "react-router-dom";
import PropTypes from "prop-types";
import { useState } from "react";
import useGlobalReducer from "../hooks/useGlobalReducer";

export const EntityDetails = ({ item, category, properties, imageUrl }) => {
  const { store, token, toggleFavorite, favoritesLoading, pendingFavorite } = useGlobalReducer();
  const navigate = useNavigate();
  const [failedImage, setFailedImage] = useState(null);

  const isFavorite = store.favorites.some(
    (favorite) =>
      favorite.category === category &&
      String(favorite.uid) === String(item.uid),
  );

  const visibleFields = Object.entries(properties).filter(
    ([field]) => !["name", "created", "edited", "url"].includes(field),
  );

  return (
    <div className="row g-4">
      <div className="col-lg-6">
        {imageUrl && failedImage !== imageUrl ? (
          <img
            src={imageUrl}
            alt={properties.name}
            className="img-fluid rounded d-block mx-auto"
            style={{ width: "auto", height: "auto", maxHeight: "500px" }}
            onError={() => setFailedImage(imageUrl)}
          />
        ) : (
          <div
            className="bg-secondary rounded d-flex align-items-center justify-content-center"
            style={{ height: "clamp(300px, 60vw, 500px)" }}
          >
            Image not available
          </div>
        )}
      </div>

      <div className="col-lg-6">
        <div className="d-flex justify-content-between align-items-center gap-3">
          <h1>{properties.name}</h1>

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
                  uid: String(item.uid),
                  name: properties.name,
              });
            }}
          >
            <span aria-hidden="true">{isFavorite ? "★" : "☆"}</span>
          </button>
        </div>

        <p className="text-body-secondary">{item.description}</p>

        <dl className="row">
          {visibleFields.map(([field, value]) => (
            <div className="col-sm-6 mb-3" key={field}>
              <dt className="text-capitalize">{field.replaceAll("_", " ")}</dt>
              <dd>{value ?? "Not available"}</dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  );
};

EntityDetails.propTypes = {
  item: PropTypes.shape({
    uid: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    description: PropTypes.string,
  }).isRequired,
  category: PropTypes.oneOf(["people", "planets", "vehicles"]).isRequired,
  properties: PropTypes.object.isRequired,
  imageUrl: PropTypes.string,
};
