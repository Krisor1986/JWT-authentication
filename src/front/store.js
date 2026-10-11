export const initialStore = () => {
  return {
    people: [],
    planets: [],
    vehicles: [],
    favorites: [],
  };
};

export default function storeReducer(store, action = {}) {
  switch (action.type) {
    case "set_people":
      return {
        ...store,
        people: action.payload,
      };
    case "set_planets":
      return {
        ...store,
        planets: action.payload,
      };

    case "set_vehicles":
      return {
        ...store,
        vehicles: action.payload,
      };
    case "set_favorites":
      return { ...store, favorites: action.payload };
    case "toggle_favorite": {
      const item = { ...action.payload, uid: String(action.payload.uid) };

      const exists = store.favorites.some(
        (favorite) =>
          favorite.category === item.category && favorite.uid === item.uid,
      );

      return {
        ...store,
        favorites: exists
          ? store.favorites.filter(
              (favorite) =>
                !(
                  favorite.category === item.category &&
                  favorite.uid === item.uid
                ),
            )
          : [...store.favorites, item],
      };
    }
    default:
      throw Error("Unknown action.");
  }
}
