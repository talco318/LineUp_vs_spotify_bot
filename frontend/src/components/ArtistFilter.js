import React, { useState } from 'react';
import { filterArtistsByWeekend } from '../apiService'; // Import the API service function

const ArtistFilter = () => {
  const [artistData, setArtistData] = useState(''); // Can be JSON string or comma-separated names
  const [weekend, setWeekend] = useState('W1');
  const [filteredArtists, setFilteredArtists] = useState([]);
  const [error, setError] = useState(null); // State to hold error information

  const handleArtistDataChange = (event) => {
    setArtistData(event.target.value);
  };

  const handleWeekendChange = (event) => {
    setWeekend(event.target.value);
  };

  const fetchFilteredArtists = async () => {
    setError(null); // Reset error state
    try {
      // Attempt to parse artistData if it's a JSON string, otherwise send as is (e.g. comma-separated string)
      let parsedArtistData;
      try {
        parsedArtistData = JSON.parse(artistData);
      } catch (e) {
        parsedArtistData = artistData; // Send as string if not valid JSON
      }
      const data = await filterArtistsByWeekend(parsedArtistData, weekend);
      setFilteredArtists(data.artists || []); // Assuming API returns { artists: [...] }
    } catch (err) {
      console.error('Error filtering artists:', err);
      setError(err.message || 'Failed to filter artists.');
      setFilteredArtists([]); // Clear artists on error
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    fetchFilteredArtists();
  };

  return (
    <div>
      {/* Remove redundant H2 as it's in App.js */}
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="artistData">Artist Data (e.g., paste JSON, or comma-separated names):</label>
          <textarea
            id="artistData"
            value={artistData}
            onChange={handleArtistDataChange}
            placeholder="Paste artist data or names"
          />
        </div>
        <div>
          <label htmlFor="weekend">Weekend:</label>
          <select id="weekend" value={weekend} onChange={handleWeekendChange}>
            <option value="W1">W1</option>
            <option value="W2">W2</option>
            <option value="W3">W3</option>
          </select>
        </div>
        <button type="submit">Filter Artists</button>
      </form>
      {error && <p className="error-message">Error: {error}</p>}
      <div className="results-area">
        <h3>Filtered Artists:</h3>
        {filteredArtists.length > 0 ? (
          <ul>
            {filteredArtists.map((artist, index) => (
              <li key={index}>{typeof artist === 'string' ? artist : artist.name || JSON.stringify(artist)}</li>
            ))}
          </ul>
        ) : (
          <p>No artists filtered yet. Submit data and weekend to filter.</p>
        )}
      </div>
    </div>
  );
};

export default ArtistFilter;
