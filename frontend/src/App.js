import './App.css';
import PlaylistProcessor from './components/PlaylistProcessor';
import LineupGenerator from './components/LineupGenerator';
import ArtistFilter from './components/ArtistFilter';
import ArtistSearch from './components/ArtistSearch';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Music Festival App</h1>
      </header>
      <main>
        <section className="component-section">
          <h2>Playlist Processor</h2>
          <PlaylistProcessor />
        </section>
        <section className="component-section">
          <h2>Lineup Generator</h2>
          <LineupGenerator />
        </section>
        <section className="component-section">
          <h2>Artist Filter</h2>
          <ArtistFilter />
        </section>
        <section className="component-section">
          <h2>Artist Search</h2>
          <ArtistSearch />
        </section>
      </main>
    </div>
  );
}

export default App;
