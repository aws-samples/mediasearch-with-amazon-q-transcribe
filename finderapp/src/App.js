import '@aws-amplify/ui-react/styles.css';
import { Route, Routes } from 'react-router-dom';
import Home from './routes/home';
import Playground from './routes/playground';

function App() {
  return (
    <Routes>
      <Route index element={<Home />} />
      <Route path="/playground" element={<Playground />} />
      <Route path="*" element={<Home />} />
    </Routes>
  );
}

export default App;
