import React, { useState } from 'react';
import { generateLineup } from '../apiService'; // Import the API service function

const LineupGenerator = () => {
  const [artistNames, setArtistNames] = useState('');
  const [weekend, setWeekend] = useState('W1');
  const [lineup, setLineup] = useState(null);
  const [error, setError] = useState(null); // State to hold error information

  const handleArtistNamesChange = (event) => {
    setArtistNames(event.target.value);
  };

  const handleWeekendChange = (event) => {
    setWeekend(event.target.value);
  };

  const fetchLineup = async () => {
    setError(null); // Reset error state
    try {
      const data = await generateLineup(artistNames, weekend);
      setLineup(data); // Assuming the API returns the full lineup data
    } catch (err) {
      console.error('Error generating lineup:', err);
      setError(err.message || 'Failed to generate lineup.');
      setLineup(null); // Clear lineup on error
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    fetchLineup();
  };

  return (
    <div>
      {/* Remove redundant H2 as it's in App.js */}
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="artistNames">Artist Names (comma-separated):</label>
          <textarea
            id="artistNames"
            value={artistNames}
            onChange={handleArtistNamesChange}
            placeholder="Enter artist names"
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
        <button type="submit">Generate Lineup</button>
      </form>
      {error && <p className="error-message">Error: {error}</p>}
      <div className="results-area">
        <h3>Generated Lineup:</h3>
        {lineup ? (
          <pre>{JSON.stringify(lineup, null, 2)}</pre>
        ) : (
          <p>No lineup generated yet. Submit artists and weekend to generate.</p>
        )}
      </div>
    </div>
  );
};

export default LineupGenerator;
