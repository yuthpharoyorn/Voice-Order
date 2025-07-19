
import './App.css';
import Navbar from './Navbar.js';
import Menu from './Menu.js';

function App() {
  return (
    <div className="app-container">
      <div className="top-side">
        <h1>Customize Your Own Menu</h1>
      </div>
      <div className="main-content">
        <div className="left-side">
          <Navbar />
        </div>
        <div className="content">
          <Menu />
        </div>
      </div>
    </div>
  );
}

export default App;


