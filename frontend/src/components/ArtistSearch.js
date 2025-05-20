import React, { useState } from 'react';
import { getArtistByName } from '../apiService'; // Import the API service function

const ArtistSearch = () => {
  const [artistName, setArtistName] = useState('');
  const [artistData, setArtistData] = useState(null);
  const [error, setError] = useState(null); // State to hold error information

  const handleInputChange = (event) => {
    setArtistName(event.target.value);
  };

  const fetchArtistData = async () => {
    setError(null); // Reset error state
    if (!artistName.trim()) {
      setError("Please enter an artist name.");
      setArtistData(null);
      return;
    }
    try {
      const data = await getArtistByName(artistName);
      setArtistData(data); // Assuming API returns the artist data object
    } catch (err) {
      console.error('Error fetching artist data:', err);
      setError(err.message || 'Failed to fetch artist data.');
      setArtistData(null); // Clear data on error
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    fetchArtistData();
  };

  return (
    <div>
      {/* Remove redundant H2 as it's in App.js */}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={artistName}
          onChange={handleInputChange}
          placeholder="Enter artist name"
        />
        <button type="submit">Search</button>
      </form>
      {error && <p className="error-message">Error: {error}</p>}
      <div className="results-area">
        <h3>Artist Details:</h3>
        {artistData ? (
          <pre>{JSON.stringify(artistData, null, 2)}</pre>
        ) : (
          <p>No artist data to display. Enter a name and search.</p>
        )}
      </div>
    </div>
  );
};

export default ArtistSearch;
