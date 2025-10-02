import './Menu.css'

import { useEffect, useState } from 'react';
import './Menu.css';

function Menu() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/menu-items') 
      .then(res => res.json())
      .then(data => setItems(data));
  }, []);
  
  return (
    <div className="menu-container">
      {items.map(item => (
        <div key={item.id} className='item-card'>
          <img src={item.image} alt={item.name} />
          <h3>{item.name}</h3>
          <p>Price: ${item.price}</p>
          <p>Category: {item.category}</p>
        </div>
      ))}
    </div>
  );
}

export default Menu;