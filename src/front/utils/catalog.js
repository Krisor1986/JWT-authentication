export const toBlogItem = record => ({
    ...record,
    uid: String(record.id),
    properties: { ...record.properties, name: record.name, ...(record.homeworld ? { homeworld: record.homeworld } : {}) }
});
