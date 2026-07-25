
// Importing 'useEffect' and 'useState' from React. 
// These are called "Hooks". They let us hook into React's engine.
import { useEffect, useState } from 'react'

// Axios is a library used to make HTTP requests (like fetching JSON data).
import axios from 'axios'

// We import the Stage (the canvas) and Graphics (a drawing tool) from PixiJS React.
import { Stage, Graphics } from '@pixi/react'
import * as PIXI from 'pixi.js'

// Basically dataclasses.
interface Zone {
  name: string
  x: number
  y: number
  type: string
  color: string
}

interface Connection {
  name1: string
  name2: string
}

// In React, a UI is built out of "Components". A component is just a function that returns HTML/JSX.
// This 'App' function is the root of our entire web page.
export default function App() {
  
  // 'useState' creates a variable that React watches. 
  // If we change it, React automatically redraws the screen.
  // It returns the variable 'zones', and a function to update it.
  const [zones, setZones] = useState<Zone[]>([]) 
  const [connections, setConnections] = useState<Connection[]>([])
  const [loading, setLoading] = useState(true) // Starts as 'true' because we have to download the data.

  // 'useEffect' runs a piece of code automatically when the component first appears on screen.
  // The empty array '[]' at the end means "only run this exactly once when the page loads".
  // Basically __init__()
  useEffect(() => {
    // Ask the Python FastAPI server for the data
    axios.get('http://127.0.0.1:8000/api/simulation')
      .then(response => {
        // If it succeeds, save the zones and connections into our React State.
        setZones(response.data.network.zones)
        setConnections(response.data.network.connections)
        
        // Tell React we are done loading so it can draw the graphics.
        setLoading(false)
      })
      .catch(error => {
        // If it fails (e.g., Python server isn't running), log an error to the browser console (F12)
        console.error("Error fetching data! Is the Python server running?", error)
      })
  }, [])

  // === LOADING SCREEN ===
  // If the data hasn't arrived yet, return this simple HTML instead of the canvas.
  if (loading) {
    return (
      <div style={{ backgroundColor: '#1e1e1e', color: 'white', width: '100vw', height: '100vh', padding: 20, fontFamily: 'sans-serif' }}>
        Loading simulation data... <br/><br/>
        (Make sure you ran <code>python -m src maps/easy/01_linear_path.txt --renderer web</code> in another terminal.)
      </div>
    )
  }

  // Helper function:
  // Convert map's grid coordinates (like x: 1, y: 0) into pixel coordinates on the screen.
  // Scale the grid by 80 pixels, and add 400 pixels to shift everything towards the center of the screen.
  const getPixels = (x: number, y: number) => {
    return { 
      px: x * 80 + 400, 
      py: -y * 80 + 400 // Negative Y because screens draw Y downwards, but math graphs go upwards.
    }
  }

  // === RENDER UI ===
  // A React component must return JSX (HTML-like + inject variables using {}).
  return (
    // A full screen div with a dark background.
    <div style={{ width: '100vw', height: '100vh', backgroundColor: '#1e1e1e' }}>
      
      {/* The Stage is the WebGL Canvas provided by PixiJS */}
      <Stage width={1200} height={800} options={{ backgroundColor: 0x1e1e1e, antialias: true }}>
        
        {/* Using '.map()' - basically for loop. For every 'zone' in our 'zones' array, we draw a <Graphics> object */}
        {zones.map((zone) => {
          // Calculate the pixels for this specific zone.
          const { px, py } = getPixels(zone.x, zone.y)
          
          return (
            <Graphics 
              key={zone.name} // React needs a unique key for items in a list.
              
              // The 'draw' function gives us a raw Pixi Graphics object 'g' to draw shapes on.
              draw={(g) => {
                g.clear() // Clear previous frame.
                
                // Draw a white outline.
                g.lineStyle(2, 0xffffff)
                
                // Fill the circle with a dark gray color.
                g.beginFill(0x333333) 
                
                // Draw the circle at the pixel coordinates with a radius of 20.
                g.drawCircle(px, py, 20)
                
                g.endFill()
              }}
            />
          )
        })}

      </Stage>
    </div>
  )
}
