import { BrowserRouter } from "react-router-dom";
import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/layout/Layout";
import Analysis from "./pages/Analysis";
import Prediction from "./pages/Prediction";

function App() {

  return (
    <div>
      <BrowserRouter>
          <Routes>
              <Route path="/" element={<Layout />}>
                  <Route index element={<Navigate to="/analysis" />} />
                  <Route path="analysis" element={<Analysis />} />
                  <Route path="prediction" element={<Prediction />} />
              </Route>
          </Routes>
      </BrowserRouter>
    </div>
  )
}

export default App
