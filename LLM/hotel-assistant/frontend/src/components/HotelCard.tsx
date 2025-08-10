interface Hotel {
  id: string;
  title: string;
  description: string;
  amenities: Record<string, string[]>;
  location: { lat: number; lon: number };
  highlights: string[];
  local_tips: string[];
  url: string;
}

interface HotelCardProps {
  hotel: Hotel;
}

export default function HotelCard({ hotel }: HotelCardProps) {
  const truncateText = (text: string, maxLength: number) => {
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  const formatAmenities = (amenities: Record<string, string[]>) => {
    const amenityList: string[] = [];
    Object.entries(amenities).forEach(([category, items]) => {
      if (Array.isArray(items) && items.length > 0) {
        amenityList.push(...items);
      }
    });
    return amenityList.slice(0, 5); // Show max 5 amenities
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <h4 className="font-semibold text-gray-800 mb-2">{hotel.title}</h4>
      
      {hotel.description && (
        <p className="text-sm text-gray-600 mb-3">
          {truncateText(hotel.description, 150)}
        </p>
      )}

      {hotel.highlights.length > 0 && (
        <div className="mb-3">
          <h5 className="text-xs font-medium text-gray-700 mb-1">Highlights:</h5>
          <div className="flex flex-wrap gap-1">
            {hotel.highlights.slice(0, 3).map((highlight, index) => (
              <span
                key={index}
                className="bg-blue-50 text-blue-700 px-2 py-1 rounded text-xs"
              >
                {highlight}
              </span>
            ))}
          </div>
        </div>
      )}

      {Object.keys(hotel.amenities).length > 0 && (
        <div className="mb-3">
          <h5 className="text-xs font-medium text-gray-700 mb-1">Amenities:</h5>
          <div className="flex flex-wrap gap-1">
            {formatAmenities(hotel.amenities).map((amenity, index) => (
              <span
                key={index}
                className="bg-green-50 text-green-700 px-2 py-1 rounded text-xs"
              >
                {amenity}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="text-xs text-gray-500 mt-2">
        <span>📍 {hotel.location.lat.toFixed(4)}, {hotel.location.lon.toFixed(4)}</span>
      </div>

      {hotel.url && (
        <div className="mt-3">
          <a
            href={hotel.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-blue-500 hover:text-blue-700 underline"
          >
            View Details →
          </a>
        </div>
      )}
    </div>
  );
}