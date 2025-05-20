import React, { useState } from 'react';
import { processPlaylist } from '../apiService'; // Import the API service function

const PlaylistProcessor = () => {
  const [playlistUrl, setPlaylistUrl] = useState('');
  const [artists, setArtists] = useState([]);
  const [error, setError] = useState(null); // State to hold error information

  const handleInputChange = (event) => {
    setPlaylistUrl(event.target.value);
  };

  const fetchArtists = async () => {
    setError(null); // Reset error state before new API call
    try {
      const data = await processPlaylist(playlistUrl);
      setArtists(data.artists || []); // Assuming the API returns { artists: [...] }
    } catch (err) {
      console.error('Error processing playlist:', err);
      setError(err.message || 'Failed to fetch artists.'); // Set error state
      setArtists([]); // Clear artists on error
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    fetchArtists();
  };

  return (
    <div>
      {/* Remove redundant H2 as it's in App.js */}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={playlistUrl}
          onChange={handleInputChange}
          placeholder="Enter playlist URL"
        />
        <button type="submit">Submit</button>
      </form>
      {error && <p className="error-message">Error: {error}</p>}
      <div className="results-area">
        <h3>Processed Artists:</h3>
        {artists.length > 0 ? (
          <ul>
            {artists.map((artist, index) => (
              // Assuming artist object has a 'name' property
              <li key={index}>{typeof artist === 'string' ? artist : artist.name || JSON.stringify(artist)}</li>
            ))}
          </ul>
        ) : (
          <p>No artists to display. Submit a URL to process.</p>
        )}
      </div>
    </div>
  );
};

export default PlaylistProcessor;
