import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { FormPage } from "./pages/form";
import { GraphicPage } from './pages/graphic';
import { Navigation } from './pages/navigation';

export function App() {

  return (
    <Router>
      <Routes>
        <Route path="/" Component={Navigation} />
        <Route path="/form" Component={FormPage} />
        <Route path="/graphic" Component={GraphicPage} />
      </Routes>
    </Router>
  )
}