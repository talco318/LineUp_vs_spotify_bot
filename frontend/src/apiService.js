import axios from 'axios';

// Set the base URL for all axios requests
axios.defaults.baseURL = 'http://localhost:5000';

/**
 * Processes a playlist URL to extract artists.
 * @param {string} playlistUrl - The URL of the playlist.
 * @returns {Promise<object>} The response data from the API.
 */
export const processPlaylist = async (playlistUrl) => {
  try {
    const response = await axios.post('/api/process-playlist', { url: playlistUrl });
    return response.data;
  } catch (error) {
    console.error('Error processing playlist:', error);
    // Optionally re-throw the error or return a specific error structure
    throw error; 
  }
};

/**
 * Generates a lineup based on a list of artists and a selected weekend.
 * @param {string} artistsStr - A string containing artist names, comma-separated.
 * @param {string} weekend - The selected weekend (e.g., 'W1', 'W2').
 * @returns {Promise<object>} The response data from the API.
 */
export const generateLineup = async (artistsStr, weekend) => {
  try {
    const response = await axios.post('/api/generate-lineup', { artists_str: artistsStr, weekend: weekend });
    return response.data;
  } catch (error) {
    console.error('Error generating lineup:', error);
    throw error;
  }
};

/**
 * Filters a list of artists by a selected weekend.
 * @param {Array<object>|string} artists - An array of artist objects or a string of artist data.
 * @param {string} weekend - The selected weekend.
 * @returns {Promise<object>} The response data from the API.
 */
export const filterArtistsByWeekend = async (artists, weekend) => {
  try {
    const response = await axios.post('/api/artists-by-weekend', { artists: artists, weekend: weekend });
    return response.data;
  } catch (error) {
    console.error('Error filtering artists by weekend:', error);
    throw error;
  }
};

/**
 * Fetches details for a specific artist by name.
 * @param {string} artistName - The name of the artist to search for.
 * @returns {Promise<object>} The response data from the API.
 */
export const getArtistByName = async (artistName) => {
  try {
    const response = await axios.post('/api/get-artist-by-name', { artist_name: artistName });
    return response.data;
  } catch (error)
 {
    console.error('Error getting artist by name:', error);
    throw error;
  }
};
